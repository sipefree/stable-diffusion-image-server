from redis.asyncio import Redis
from sanic import Sanic
from typing import NewType
from pathlib import Path

class DBService:
    
    def __init__(self, conn: Redis, app: Sanic):
        self.conn = conn
        self.app = app
        
    @property
    def basepath(self) -> Path:
        """The base path of all the content files."""
        return Path(self.app.config.IMAGE_DIR)
    
    def pathstem(self, full_path: Path) -> str:
        """
        Returns the suffix of fullpath which is relative to the base path.
        
        e.g. If basepath is Path('/sdis-content'), and fullpath is
        Path('/sdis-content/txt2img-images/2023-06-01'), then it returns
        'txt2img-images/2023-06-01'
        """
        return str(full_path.relative_to(self.basepath))