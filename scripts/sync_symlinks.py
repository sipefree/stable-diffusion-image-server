#!/usr/bin/env python

import argparse
import os
import sys
import asyncio
from typing import Callable
from pathlib import Path

from pathlib import Path
from asyncinotify import Inotify, Mask
import asyncio
from typing import Callable

async def watch_dirs_apply(dir_paths: list[Path], fn: Callable[[Path], None]) -> None:
    """
    Watches the provided directory paths for changes and calls the provided function with the
    source directory of the event. The function is called asynchronously.

    Parameters:
        dir_paths: A list of directory paths to watch.
        fn: A function that accepts a single Path argument.
    """
    # Create an Inotify instance to monitor the directories
    with Inotify() as inotify:
        
        # Dictionary to keep track of watches and their corresponding directory paths
        watches = {}
        
        # Create a mask for the desired events: CREATE, DELETE, MOVE
        mask = Mask.CREATE | Mask.DELETE | Mask.MOVE
        
        # Add watches for each directory path and store in the dictionary
        for dir_path in dir_paths:
            print(f"+ Adding watch for: {dir_path}")
            watch = inotify.add_watch(dir_path, mask)
            watches[watch] = dir_path
        
        # Monitor for events asynchronously
        async for event in inotify:
            # Determine the source directory for the event based on its watch
            source_dir = watches.get(event.watch)
            
            if source_dir:
                # Call the provided function with the source directory
                fn(source_dir)

def watch_dirs_apply_forever(dir_paths: list[Path], fn: Callable[[Path], None]) -> None:
    """
    Watches the provided directory paths for changes and calls the provided function with the
    source directory of the event. The function is called asynchronously.
    
    This function creates an event loop for this process and never returns.

    Parameters:
        dir_paths: A list of directory paths to watch.
        fn: A function that accepts a single Path argument.
    """
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(watch_dirs_apply(dir_paths, fn))
    except KeyboardInterrupt:
        print('shutting down')
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

def buffer_fn(fn: Callable[[Path], None]) -> Callable[[Path], None]:
    """
    Returns a function that debounces and buffers calls to the provided function.
    The returned function will wait for 1 second after the first call before calling
    the provided function. Any calls made during that 1 second will be ignored.

    Parameters:
        fn: A function that accepts a single Path argument.

    Returns:
        A function that accepts a single Path argument.
    """
    buffer_timers: dict[Path, asyncio.TimerHandle] = {}

    async def buffered_call(path: Path):
        # Wait for 1 second (or desired debounce time)
        print(f"  (Debouncing for 1 second: {path})")
        await asyncio.sleep(1)
        
        # Call the original function
        print(f"- Syncing after filesystem events: {path}")
        fn(path)

        # Remove the path from the buffer_timers dict
        buffer_timers.pop(path, None)

    def wrapper(path: Path) -> None:
        # Cancel the existing timer if it exists
        if path in buffer_timers:
            print(f"  (Canceling existing timer for: {path})")
            buffer_timers[path].cancel()
            
        # Start the buffered call as a task and store its timer
        buffer_timers[path] = asyncio.ensure_future(buffered_call(path))

    return wrapper

def sync_symlinks(src_dir: Path, dst_dir: Path):
    """
    Synchronizes a source directory with a destination directory by
    creating or updating symbolic links.

    Args:
        src_dir (str): The path to a source directory.
        dst_dir (str): The path to the destination directory.

    Raises:
        SystemExit: If the destination directory does not exist.
    """
    print(f"Syncing symlinks from {src_dir} to {dst_dir}.")
    do_sync_links(get_src_files(src_dir), dst_dir)

def do_sync_links(src_files: dict[str, Path], dst_dir: Path):
    """
    Synchronizes a dictionary of source files with a destination directory by
    creating or updating symbolic links.

    Args:
        src_files (dict[str, Path]): A dictionary of source files, where the keys
                                     are the file names and the values are the Path objects.
        dst_dir (Path): The Path object to the destination directory.

    Raises:
        SystemExit: If the destination directory does not exist.
    """
    if not dst_dir.is_dir():
        print(f"Destination directory does not exist: {dst_dir}")
        sys.exit(1)
        
    src_files = {k: relative_path_from_to(v, dst_dir) for k, v in src_files.items()}
        
    existing_symlinks = set()  # Existing, correct symlinks
    for file_name in dst_dir.iterdir():
        if file_name.is_symlink():
            target_path = file_name.resolve(strict=False)
            if str(file_name.name) in src_files and src_files[str(file_name.name)] == target_path:
                existing_symlinks.add(str(file_name.name))
            else:
                print(f"Deleting broken symlink: {file_name}")
                file_name.unlink()

    for file_name, src_path in src_files.items():
        if file_name not in existing_symlinks:
            dst_path = dst_dir / file_name
            print(f"Creating new symlink: {dst_path} -> {src_path}")
            dst_path.symlink_to(src_path)

def relative_path_from_to(src: Path, dst: Path) -> Path:
    """
    Get a relative path to go from dst to src.
    """
    src_parts = src.resolve().parts
    dst_parts = dst.resolve().parts

    # Find common ancestor
    common_length = len(os.path.commonprefix([src_parts, dst_parts]))
    to_common = ['..'] * (len(dst_parts) - common_length)

    # Return relative path
    return Path(*to_common, *src_parts[common_length:])

def get_src_files(src_dir: Path) -> dict[str, Path]:
    """
    Returns a dictionary of source files in a directory, where
    the keys are the file names and the values are the Path objects.

    Args:
        src_dir (Path): The Path object to the source directory.

    Raises:
        SystemExit: If the source directory does not exist.

    Returns:
        dict[str, Path]: A dictionary of source files, where the keys are
                         the file names and the values are the Path objects.

    """
    src_files = {}  # Original file paths keyed by file name

    if not src_dir.is_dir():
        print(f"Source directory does not exist: {src_dir}")
        sys.exit(1)

    for file_path in src_dir.iterdir():
        if file_path.is_file():
            src_files[file_path.name] = file_path
    return src_files

def get_src_files_multi(src_dirs: list[Path]) -> dict[str, Path]:
    """
    Returns a dictionary of source files in multiple directories, where
    the keys are the file names and the values are the Path objects.

    Args:
        src_dirs (list[Path]): A list of Path objects to the source directories.

    Returns:
        dict[str, Path]: A dictionary of source files, where the keys are
                         the file names and the values are the Path objects.

    """
    src_files = {}  # Original file paths keyed by file name
    for src_dir in src_dirs:
        dir_src_files = get_src_files(src_dir)
        for file_name, file_path in dir_src_files.items():
            if file_name not in src_files:  # Ignore duplicate file names
                src_files[file_name] = file_path
            else:
                print(f"Duplicate file name found, ignoring: {file_path}")
    return src_files

def main():
    parser = argparse.ArgumentParser(description="Synchronize symlinks from source to destination directories.")
    parser.add_argument("dir_pairs", metavar="SRC:DST", type=str, nargs='+', help="Colon-separated pairs of source and destination directories.")
    parser.add_argument("--watch", action="store_true", help="Keep watching the source directories for changes.")

    args = parser.parse_args()

    # Collecting unique source and destination directories from the pairs
    src_dirs = []
    dst_dirs = {}
    for dir_pair in args.dir_pairs:
        src, dst = dir_pair.split(':')
        src_path = Path(src)
        dst_path = Path(dst)

        if src_path in src_dirs or dst_path in dst_dirs.values():
            print(f"Error: Duplicate source or destination directory found: {src} or {dst}")
            sys.exit(1)

        if not src_path.is_dir():
            print(f"Error: Source directory does not exist: {src_path}")
            sys.exit(1)
            
        if not dst_path.is_dir():
            if dst_path.parent.is_dir():
                dst_path.mkdir()
            else:
                print(f"Error: Parent of destination directory does not exist: {dst_path.parent}")
                sys.exit(1)

        src_dirs.append(src_path)
        dst_dirs[src] = dst_path

    # Perform the initial sync
    for src in src_dirs:
        sync_symlinks(src, dst_dirs[str(src)])

    # If --watch is used, watch the directories
    if args.watch:
        def callback(src_path: Path):
            sync_symlinks(src_path, dst_dirs[str(src_path)])

        debounced_callback = buffer_fn(callback)
        watch_dirs_apply_forever(src_dirs, debounced_callback)

if __name__ == "__main__":
    main()