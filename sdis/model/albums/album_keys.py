from .album import Album, AlbumLike
from ..service import DBBase

import re
from pathlib import Path

# ---------------------------------------------------------------------------- #
#                               Album Keys Class                               #
# ---------------------------------------------------------------------------- #

class AlbumKeys(DBBase):
    """A utility class that provides methods for generating Redis keys for Albums."""

    _album_key_regex = re.compile(r"album:([^:]+)")

    def resolve_stem(self, album: AlbumLike) -> str:
        """Returns the path stem for the given Album, Path, or str."""
        if isinstance(album, Album):
            return self.pathstem(album.original_path)
        elif isinstance(album, Path):
            return self.pathstem(album)
        elif isinstance(album, str): # type: ignore
            match = AlbumKeys._album_key_regex.match(album)
            if match:
                return match.group(1)
            elif album.startswith("/"):
                return self.resolve_stem(Path(album))
            else:
                return self.quotepath(self.unquotepath(album))
        else:
            raise ValueError("Must pass either Album, Path, or str.")

    # --------------------------------- Redis Keys --------------------------------- #

    def album_key(self, album: AlbumLike) -> str:
        """Returns the Redis key for the Album."""
        return f"album:{self.resolve_stem(album)}"

    def subalbums_key(self, album: AlbumLike) -> str:
        """Returns the Redis key for the Album's subalbum set."""
        return f"album_subalbums:{self.resolve_stem(album)}"

    def images_key(self, album: AlbumLike) -> str:
        """Returns the Redis key for the Album's image set."""
        return f"album_images:{self.resolve_stem(album)}"