import redis.asyncio
from sanic import DefaultSanic
from typing import cast, Union
from pathlib import Path
from pathlib import Path
import cattrs
from urllib.parse import quote, unquote

from pendulum.datetime import DateTime
from pendulum.parser import parse as pendulum_parse

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
    def __init__(self, conn: redis.asyncio.Redis, app: DefaultSanic):
        super().__init__(basepath=Path(cast(str, app.config['IMAGE_DIR'])))
        self.conn: redis.asyncio.Redis = conn
        self.app: DefaultSanic = app
        app.ext.dep
        
    
    