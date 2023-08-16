from attrs import define, field, validators
from typing import Optional, Union, ClassVar
from pathlib import Path
from .service import DBService, DBBase
from pendulum.datetime import DateTime
import pendulum
import cattrs
import re

@define
class Album:
    id: str                         = field()
    name: str                       = field(validator=validators.min_len(1))
    original_path: Path             = field()
    generated_path: Path            = field()
    thumbnail_path: Optional[Path]  = field()
    creation_timestamp: DateTime    = field()
    
    # ---------------------------------------------------------------------------- #
    
    @classmethod
    def load_from_path(cls, path: Path, basepath: Path, gen_basepath: Path) -> 'Album':
        keys = AlbumKeys(basepath=basepath)
        full_path = path.resolve()
        return Album(
            id = keys.album_key(full_path),
            name = full_path.name,
            original_path = full_path,
            generated_path = gen_basepath / keys.pathstem(full_path),
            thumbnail_path = None,
            creation_timestamp = cls.creation_timestamp_from_path(full_path)
        )
        
    _date_regex: ClassVar[re.Pattern[str]] = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
    
    @classmethod
    def creation_timestamp_from_path(cls, path: Path) -> DateTime:
        # if the path name matches 'YYYY-MM-DD', then use that as the creation timestamp
        match = cls._date_regex.match(path.name)
        if match != None:
            year, month, day = match.groups()
            return pendulum.local(year=int(year), month=int(month), day=int(day), hour=0, minute=0, second=0)
        else:
            return pendulum.from_timestamp(path.stat().st_ctime)
        
        
        

AlbumLike = Union[Album, Path, str]

class AlbumKeys(DBBase):
    """A utility class that provides methods for generating Redis keys for Albums."""
    
    def resolve_stem(self, album: AlbumLike) -> str:
        """Returns the path stem for the given Album, Path, or str."""
        if isinstance(album, Album):
            return self.pathstem(album.original_path)
        elif isinstance(album, Path):
            return self.pathstem(album)
        elif isinstance(album, str): # type: ignore
            return album
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