# pyright: reportUnknownVariableType=false

from typing import Awaitable, Optional, cast

from ..albums import AlbumLike
from ..service import DBService
from .image import Image, ImageLike
from .image_import import ImageImport
from .image_keys import ImageKeys

# ---------------------------------------------------------------------------- #
#                              Image Service Class                             #
# ---------------------------------------------------------------------------- #

class ImageService(DBService, ImageImport, ImageKeys):
    """A database service object for Images."""
    
    # ---------------------------------- Queries --------------------------------- #
    
    async def get_image(self, image: ImageLike) -> Optional[Image]:
        """Returns the Image object for the given Image, Path, or str."""
        return await self.get_object(Image, self.image_key(image))
    
    