from attrs import define, field, validators
from typing import Optional, Any, Union
from datetime import datetime
from pathlib import Path
from typing import Union
from redis.asyncio import Redis
from .service import DBService
import cattrs

@define
class Album:
    id: str                         = field()
    name: str                       = field(validator=validators.min_len(1))
    original_path: Path             = field(converter=Path)
    generated_path: Path            = field(converter=Path)
    thumbnail_path: Path            = field(converter=Path)
    creation_timestamp: datetime    = field()
    
    @classmethod
    def load_from_path(path: Path):
        keys = AlbumKeys()
        full_path = path.resolved()
        id = keys.)
        
        

AlbumLike = Union[Album, Path, str]

class AlbumKeys:
    """A utility class that provides methods for generating Redis keys for Albums."""
    
    def resolve_stem(self, album: AlbumLike):
        """Returns the path stem for the given Album, Path, or str."""
        if isinstance(album, Album):
            return self.pathstem(album.original_path)
        elif isinstance(album, Path):
            return self.pathstem(Path)
        elif isinstance(album, str):
            return str
        else:
            raise ValueError("Must pass either Album, Path, or str.")
        
    # --------------------------------- Redis Keys --------------------------------- #
        
    def album_key(self, album: AlbumLike) -> str:
        """Returns the Redis key for the Album."""
        return f"album:{self.resolve_stem(album)}"
    
    def subalbums_key(self, album: AlbumLike) -> str:
        """Returns the Redis key for the Album's subalbum set."""
        return f"album_subalbums:{self.resolve_stem(album)}"
    
    def images_key(self, album: AlbumLike) -> str:
        """Returns the Redis key for the Album's image set."""
        return f"album_images:{self.resolve_stem(album)}"

class AlbumService(DBService, AlbumKeys):
    """A database service object for Albums."""
    
    # ---------------------------------- Queries --------------------------------- #
    
    async def get_album(self, album: AlbumLike) -> Optional[Album]:
        """Returns the Album object for the given Album, Path, or str."""
        res = await self.conn.json().get(self.album_key(album))
    
    
    
    
    
    
        
"""
@register
class SelectAlbums(SQLiteExecutor):
    @query("SELECT * FROM albums ORDER BY $order_by LIMIT $limit OFFSET $offset")
    async def select_albums(self, order_by: str = "name", limit: int = 100000, offset: int = 0) -> list[Album]:
        ...

@register
class SelectAlbum(SQLiteExecutor):
    @query("SELECT * FROM albums WHERE id = $id")
    async def select_album(self, id: int) -> Optional[Album]:
        ...

@register
class SelectAlbumsOfParent(SQLiteExecutor):
    @query("SELECT * FROM albums WHERE parent_id = $parent_id ORDER BY $order_by LIMIT $limit OFFSET $offset")
    async def select_albums_of_parent(self, parent_id: int, order_by: str = "name", limit: int = 100000, offset: int = 0) -> list[Album]:
        ...

@register
class InsertAlbum(SQLiteExecutor):
    @query("INSERT INTO albums (name, original_path, generated_path, parent_id, thumbnail_path, creation_timestamp) VALUES ($name, $original_path, $generated_path, $parent_id, $thumbnail_path, $creation_timestamp)")
    async def insert_album(self, name: str, original_path: Path, generated_path: Path, parent_id: Optional[int], thumbnail_path: Path, creation_timestamp: datetime) -> int:
        ...
"""