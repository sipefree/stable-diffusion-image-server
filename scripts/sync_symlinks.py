import argparse
import os
import sys
import asyncio
from typing import Callable
from pathlib import Path

from pathlib import Path
from asyncinotify import Inotify, Mask
import asyncio
from typing import Callable, List

async def watch_dirs_apply(dir_paths: List[Path], fn: Callable[[Path], None]) -> None:
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
            watch = inotify.add_watch(dir_path, mask)
            watches[watch] = dir_path
        
        # Monitor for events asynchronously
        async for event in inotify:
            # Determine the source directory for the event based on its watch
            source_dir = watches.get(event.watch)
            
            if source_dir:
                # Call the provided function with the source directory
                fn(source_dir)

def watch_dirs_apply_forever(dir_paths: List[Path], fn: Callable[[Path], None]) -> None:
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
        # Cancel the existing timer if it exists
        if path in buffer_timers:
            buffer_timers[path].cancel()

        # Wait for 1 second (or desired debounce time)
        await asyncio.sleep(1)
        
        # Call the original function
        fn(path)

        # Remove the path from the buffer_timers dict
        buffer_timers.pop(path, None)

    def wrapper(path: Path) -> None:
        # Start the buffered call as a task and store its timer
        buffer_timers[path] = asyncio.ensure_future(buffered_call(path))

    return wrapper

def sync_symlinks(src_dir: str, dst_dir: str):
    """
    Sync symlinks
    """
    print(f"Syncing symlinks from {src_dir} to {dst_dir}.")
    do_sync_links(get_src_files(src_dir), dst_dir)

def do_sync_links(src_files: dict[str, str], dst_dir: str):
    if not os.path.isdir():
        print(f"Destination directory does not exist: {dst_dir}")
        sys.exit(1)
        
    existing_symlinks = set()  # Existing, correct symlinks
    for file_name in os.listdir(dst_dir):
        full_path = os.path.join(dst_dir, file_name)
        if os.path.islink(full_path):
            target_path = os.readlink(full_path)
            if file_name in src_files and src_files[file_name] == target_path:
                existing_symlinks.add(file_name)
            else:
                print(f"Deleting broken symlink: {full_path}")
                os.unlink(full_path)

    for file_name, src_path in src_files.items():
        if file_name not in existing_symlinks:
            dst_path = os.path.join(dst_dir, file_name)
            print(f"Creating new symlink: {dst_path}")
            os.symlink(src_path, dst_path)

def get_src_files(src_dir: str) -> dict[str, str]:
    src_files = {} # Original file paths keyed by file name
    src_dir = os.path.abspath(src_dir)
    if not os.path.isdir(src_dir):
        print(f"Source directory does not exist: {src_dir}")
        sys.exit(1)
    for file_name in os.listdir(src_dir):
        full_path = os.path.join(src_dir, file_name)
        if os.path.isfile(full_path):
            src_files[file_name] = full_path

def get_src_files_multi(src_dirs: list[str]) -> dict[str, str]:
    src_files = {} # Original file paths keyed by file name
    for src_dir in src_dirs:
        dir_src_files = get_src_files(src_dir)
        for file_name, full_path in dir_src_files.items():
            if file_name not in src_files:  # Ignore duplicate file names
                src_files[file_name] = full_path
            else:
                print(f"Duplicate file name found, ignoring: {full_path}")