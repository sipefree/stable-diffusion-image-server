from pathlib import Path
from typing import Awaitable, TypeVar, Union, cast, Optional, Type
from urllib.parse import quote, unquote

import cattrs
import redis.asyncio
from pendulum.datetime import DateTime
from pendulum.parser import parse as pendulum_parse
from sanic import DefaultSanic

from .async_json import AsyncJSONCommands, JsonType

T = TypeVar('T')

def cast_async(value: T) -> Awaitable[T]:
    return cast(Awaitable[T], value)

class DBBase:
    def __init__(self, basepath: Path):
        self.basepath: Path = basepath
        
    def pathstem(self, full_path: Path) -> str:
        """
        Returns the suffix of fullpath which is relative to the base path.
        
        e.g. If basepath is Path('/sdis-content'), and fullpath is
        Path('/sdis-content/txt2img-images/2023-06-01'), then it returns
        'txt2img-images/2023-06-01'
        """
        return self.quotepath(str(full_path.relative_to(self.basepath)))
    
    def quotepath(self, path: Union[Path, str]) -> str:
        """Returns the path, with special characters escaped."""
        return quote(str(path), safe=" /")
    
    def unquotepath(self, path: str) -> str:
        """Returns the path, with special characters unescaped."""
        return unquote(path)
    
    @classmethod
    def make_converter(cls):
        converter = cattrs.Converter()
        converter.register_structure_hook(DateTime, lambda dt, _: pendulum_parse(dt))
        converter.register_unstructure_hook(DateTime, lambda dt: dt.to_iso8601_string())
        return converter


class DBService(DBBase):
    """Base class for services that use redis."""
    
    def __init__(self, conn: redis.asyncio.Redis, app: DefaultSanic):
        super().__init__(basepath=Path(cast(str, app.config['IMAGE_DIR'])))
        self.conn: redis.asyncio.Redis = conn
        self.app: DefaultSanic = app
        self.json: AsyncJSONCommands = cast(AsyncJSONCommands, self.conn.json())
        self.converter = self.__class__.make_converter()
        self.configure_converter(self.converter)
    
    def configure_converter(self, converter: cattrs.Converter):
        """Override this method to configure the converter."""
        pass
    
    def structure_one(self, json_result: list[JsonType], cls: Type[T]) -> Optional[T]:
        """Converts a single JSON result to an object."""
        if len(json_result) == 0:
            return None
        return self.converter.structure(json_result[0], cls)
    
    def structure_many(self, json_result: list[JsonType], cls: Type[T]) -> list[T]:
        """Converts a list of JSON results to a list of objects."""
        return [self.converter.structure(item, cls) for item in json_result]
        