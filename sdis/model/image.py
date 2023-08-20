from attrs import define, field, validators
from typing import Optional, Any, Union
from pendulum.datetime import DateTime
import pendulum
import json
from pathlib import Path
from .service import DBBase, DBService
import re

ParamType = Union[str, int, float]
ParamDict = dict[str, ParamType]

# ---------------------------------------------------------------------------- #
#                                  Image Class                                 #
# ---------------------------------------------------------------------------- #

@define
class Image:
    id: str                                 = field()
    album_id: str                           = field()
    original_path: Path                     = field(converter=Path)
    fullsize_thumbnail_path: Optional[Path] = field(converter=Path)
    large_thumbnail_path: Optional[Path]    = field(converter=Path)
    small_thumbnail_path: Optional[Path]    = field(converter=Path)
    width: int                              = field(validator=validators.ge(1))
    height: int                             = field(validator=validators.ge(1))
    creation_timestamp: DateTime            = field()
    origfile_size: int                      = field(validator=validators.ge(1))
    origfile_hash: str                      = field()
    parameters_text: str                    = field()
    parameters: ParamDict                   = field(factory=dict)


# ---------------------------------------------------------------------------- #
#                               Image Keys Class                               #
# ---------------------------------------------------------------------------- #

ImageLike = Union[Image, Path, str]

class ImageKeys(DBBase):
    """A utility class that provides methods for generating Redis keys for Images."""
    
    
    _image_id_regex = re.compile(r"image:(.+):(.+)")
    
    def resolve_stem_and_name(self, image: ImageLike) -> (str, str):
        """Returns the path stem for the given Image, Path, or str."""
        if isinstance(image, Image):
            return (self.pathstem(image.original_path), image.original_path.name)
        elif isinstance(image, Path):
            return (self.pathstem(image), image.name)
        elif isinstance(image, str): # type: ignore
            pass
        else:
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
        return f"image:{self.resolve_stem(image)}:{self.resolve_filename(image)}"
    
    def album_key(self, image: ImageLike) -> str:
        pass
# ---------------------------------------------------------------------------- #
#                              Image Service Class                             #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#                                   Utilities                                  #
# ---------------------------------------------------------------------------- #

def path_is_image(path: Path) -> bool:
    """Returns True if the given path is an image file."""
    return path.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.tiff', '.webp')