

from typing import Optional

from ..service import DBService
from .album import Album, AlbumLike
from .album_import import AlbumImport
from .album_keys import AlbumKeys
from ..images import Image

# ---------------------------------------------------------------------------- #
#                              Album Service Class                             #
# ---------------------------------------------------------------------------- #


class AlbumService(DBService, AlbumImport, AlbumKeys):
    """A database service object for Albums."""

    # ---------------------------------- Queries --------------------------------- #

    async def get_album(self, album: AlbumLike) -> Optional[Album]:
        """Returns the Album object for the given Album, Path, or str."""
        return await self.get_object(Album, self.album_key(album))
    
    async def get_subalbums(self, album: AlbumLike) -> list[Album]:
        """Returns the subalbums of the given Album, Path, or str."""
        return await self.get_objects_from_key_set(Album, self.subalbums_key(album))
    
    async def get_album_images(self, album: AlbumLike) -> list[Image]:
        """Returns the images of the given Album, Path, or str."""
        return await self.get_objects_from_key_set(Image, self.images_key(album))
    
        
    