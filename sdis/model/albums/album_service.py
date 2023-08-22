from typing import Optional

from ..service import DBService
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
        res = await self.json.get(self.album_key(album), '$')
        return self.structure_one(res, Album)
    
    async def get_subalbums(self, album: AlbumLike) -> list[Album]:
        """Returns the subalbums of the given Album, Path, or str."""
        subalbum_keys = await self.conn.smembers(self.subalbums_key(album))
        
    