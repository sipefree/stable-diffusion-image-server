from attrs import define, field, validators
from typing import Optional, Any, Union
from datetime import datetime
import json
from pathlib import Path
from mayim import SQLiteExecutor

ParamType = Union[str, int, float]
ParamDict = dict[str, ParamType]

def _convert_parameters(input: Union[str, ParamDict]) -> dict[str, Union[str, int, float]]:
    if isinstance(input, str):
        return json.loads(input)
    elif isinstance(input, dict):
        return input
    else:
        raise TypeError(f"Invalid type for parameters: {type(input)}")


@define
class Image:
    id: Optional[int]               = field(default=None)  # Autoincrement, so default is None
    album_id: int                   = field()
    original_path: Path             = field(converter=Path)
    fullsize_thumbnail_path: Path   = field(converter=Path)
    large_thumbnail_path: Path      = field(converter=Path)
    small_thumbnail_path: Path      = field(converter=Path)
    width: int                      = field(validator=validators.min(1))
    height: int                     = field(validator=validators.min(1))
    creation_timestamp: datetime    = field()
    origfile_size: int              = field(validator=validators.min(1))
    origfile_hash: str              = field()
    parameters_text: str            = field()
    parameters: ParamDict           = field(factory=dict, converter=_convert_parameters)
    