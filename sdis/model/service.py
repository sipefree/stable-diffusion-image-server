import redis
from sanic import Sanic
from typing import NewType
from pathlib import Path

class DBBase:
    def __init__(self, basepath: Path):
        self.basepath: Path = basepath

class DBService(DBBase):
    
    def __init__(self, conn: redis.asyncio.Redis, app: Sanic):
        self.conn: redis.asyncio.Redis = conn
        self.app: Sanic = app
        super().__init__(basepath=Path(self.app.config.IMAGE_DIR))
    
    def pathstem(self, full_path: Path) -> str:
        """
        Returns the suffix of fullpath which is relative to the base path.
        
        e.g. If basepath is Path('/sdis-content'), and fullpath is
        Path('/sdis-content/txt2img-images/2023-06-01'), then it returns
        'txt2img-images/2023-06-01'
        """
        return str(full_path.relative_to(self.basepath))