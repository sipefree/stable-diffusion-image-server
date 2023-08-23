from .image import Image, ImageLike
from ..service import DBBase
from ..albums import AlbumKeys

import re
from pathlib import Path

# ---------------------------------------------------------------------------- #
#                               Image Keys Class                               #
# ---------------------------------------------------------------------------- #

class ImageKeys(DBBase):
    """A utility class that provides methods for generating Redis keys for Images."""
    
    _image_id_regex = re.compile(r"image:(.+):(.+)")
    
    def resolve_stem_and_name(self, image: ImageLike) -> tuple[str, str]:
        """Returns the path stem for the given Image, Path, or str."""
        if isinstance(image, Image):
            return (self.pathstem(image.original_path), image.original_path.name)
        elif isinstance(image, Path):
            return (self.pathstem(image), image.name)
        elif isinstance(image, str): # type: ignore
            match = ImageKeys._image_id_regex.match(image)
            if match:
                return (match.group(1), match.group(2))
            elif image.startswith("/"):
                return self.resolve_stem_and_name(Path(image))
        raise ValueError("Must pass either Image, Path, or str.")
    
    def resolve_filename(self, image: ImageLike) -> str:
        """Returns the filename for the given Image, Path, or str."""
        if isinstance(image, Image):
            return image.original_path.name
        elif isinstance(image, Path):
            return image.name
        elif isinstance(image, str): # type: ignore
            return Path(image).name
        else:
            raise ValueError("Must pass either Image, Path, or str.")
        
    # --------------------------------- Redis Keys --------------------------------- #
    
    def image_key(self, image: ImageLike) -> str:
        """Returns the Redis key for the Image."""
        (stem, name) = self.resolve_stem_and_name(image)
        return f"image:{stem}:{name}"
    
    def album_key(self, image: ImageLike) -> str:
        (stem, _) = self.resolve_stem_and_name(image)
        return self._albumkeys().album_key(stem)
    
    # ---------------------------------- Private --------------------------------- #
    
    def _albumkeys(self) -> AlbumKeys:
        if not hasattr(self, "_albumkeys_obj"):
            from ..albums import AlbumKeys
            self._albumkeys_obj = AlbumKeys(basepath=self.basepath)
        return self._albumkeys_obj
        