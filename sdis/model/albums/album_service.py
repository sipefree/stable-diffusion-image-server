from typing import Optional

from ..service import DBService, cast_async
from .album import Album, AlbumLike
from .album_import import AlbumImport
from .album_keys import AlbumKeys

# ---------------------------------------------------------------------------- #
#                              Album Service Class                             #
# ---------------------------------------------------------------------------- #


class AlbumService(DBService, AlbumImport, AlbumKeys):
    """A database service object for Albums."""

    # ---------------------------------- Queries --------------------------------- #

    async def get_album(self, album: AlbumLike) -> Optional[Album]:
        """Returns the Album object for the given Album, Path, or str."""
        res = await cast_async(self.conn.json().get(self.album_key(album), '$'))