from attrs import define, field, validators
from typing import Optional, Any, Union
from datetime import datetime
from pathlib import Path
from typing import Union
from redis.asyncio import Redis
from .service import DBService

@define
class Album:
    id: str                         = field()  # Autoincrement, so default is None
    name: str                       = field(validator=validators.min_length(1))
    original_path: Path             = field(converter=Path)
    generated_path: Path            = field(converter=Path)
    parent_id: Optional[int]        = field(default=None)  # Nullable, so default is None
    thumbnail_path: Path            = field(converter=Path)
    creation_timestamp: datetime    = field()


class AlbumService(DBService):
    """A database service object for Albums."""
    
    
    
    def key_for_stem(self, pathstem: str) -> str:
        """Returns the Redis key for the Album with the given path stem."""
        return f"album:{pathstem}"
    
    def key_for_album_path(self, full_path: Path) -> str:
        """Returns the Redis key for the Album with the given full path."""
        return self.key_for_stem(self.pathstem(full_path))
    
    def key_for_album(self, album: Album) -> str:
        """Returns the Redis key for the given Album."""
        return self.key_for_album_path(album.original_path)
    
    def resolve_stem(self, album: Union[Album, Path, str]):
        """Returns the path stem for the given Album, Path, or str."""
        if isinstance(album, Album):
            return self.pathstem(album.original_path)
        elif isinstance(album, Path):
            return self.pathstem(Path)
        elif isinstance(album, str):
            return str
        else:
            raise ValueError("Must pass either Album, Path, or str.")
    
    
    # --------------------------------- Patterns --------------------------------- #
    
    @property
    def all_albums_key_pattern(self) -> str:
        """The Redis key pattern for all albums."""
        return 'album:*'
    
    def subalbums_of_album_pattern(self, album: Path) -> str:
        """The Redis key pattern for all subalbums of the given album."""
        return f"album:{relpath}/*"
    
    def subalbums_of_
    
    
    
    
        

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