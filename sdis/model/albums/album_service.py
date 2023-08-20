from .album import Album, AlbumLike
from .album_keys import AlbumKeys
from .album_import import AlbumImport
from ..service import DBService

from typing import Optional

from redis

# ---------------------------------------------------------------------------- #
#                              Album Service Class                             #
# ---------------------------------------------------------------------------- #


class AlbumService(DBService, AlbumImport, AlbumKeys):
    """A database service object for Albums."""
    
    @property
    

    # ---------------------------------- Queries --------------------------------- #

    async def get_album(self, album: AlbumLike) -> Optional[Album]:
        """Returns the Album object for the given Album, Path, or str."""
        res = await self.conn.json().get(self.album_key(album))