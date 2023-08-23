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




ImageLike = Union[Image, Path, str]





