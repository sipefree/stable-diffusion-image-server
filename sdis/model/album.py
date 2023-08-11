from attrs import define, field, validators
from typing import Optional, Any, Union
from datetime import datetime
from pathlib import Path
from mayim import SQLiteExecutor, register, query

@define
class Album:
    id: Optional[int]               = field(default=None)  # Autoincrement, so default is None
    name: str                       = field(validator=validators.min_length(1))
    original_path: Path             = field(converter=Path)
    generated_path: Path            = field(converter=Path)
    parent_id: Optional[int]        = field(default=None)  # Nullable, so default is None
    thumbnail_path: Path            = field(converter=Path)
    creation_timestamp: datetime    = field()

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