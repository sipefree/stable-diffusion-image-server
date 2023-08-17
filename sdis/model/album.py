import re
from collections import deque
from pathlib import Path
from typing import ClassVar, Optional, Union

import pendulum
from attrs import define, field, validators
from pendulum.datetime import DateTime

from .image import Image, path_is_image
from .service import DBBase, DBService

# ---------------------------------------------------------------------------- #
#                                  Album Class                                 #
# ---------------------------------------------------------------------------- #

@define
class Album:
    id: str                         = field()
    name: str                       = field(validator=validators.min_len(1))
    original_path: Path             = field()
    generated_path: Optional[Path]  = field()
    thumbnail_path: Optional[Path]  = field()
    created: DateTime               = field()


# ---------------------------------------------------------------------------- #
#                               Album Tree Class                               #
# ---------------------------------------------------------------------------- #

@define
class AlbumTree:
    album: Album                    = field()
    subalbums: list['AlbumTree']    = field(factory=list)
    images: list[Image]             = field(factory=list)
    imageCountEstimate: int         = field(default=0)
    subCountEstimate: int           = field(default=0)
    parent: 'AlbumTree'             = field(default=None)
    
    
# ---------------------------------------------------------------------------- #
#                               Album Keys Class                               #
# ---------------------------------------------------------------------------- #
        

AlbumLike = Union[Album, Path, str]

class AlbumKeys(DBBase):
    """A utility class that provides methods for generating Redis keys for Albums."""
    
    _album_key_regex = re.compile(r"album:([^:]+)")
    
    def resolve_stem(self, album: AlbumLike) -> str:
        """Returns the path stem for the given Album, Path, or str."""
        if isinstance(album, Album):
            return self.pathstem(album.original_path)
        elif isinstance(album, Path):
            return self.pathstem(album)
        elif isinstance(album, str): # type: ignore
            match = AlbumKeys._album_key_regex.match(album)
            if match:
                return match.group(1)
            elif album.startswith("/"):
                return self.resolve_stem(Path(album))
            else:
                return self.quotepath(self.unquotepath(album))
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


# ---------------------------------------------------------------------------- #
#                              Album Import Class                              #
# ---------------------------------------------------------------------------- #

class AlbumImport(AlbumKeys):
    
    _date_regex: ClassVar[re.Pattern[str]] = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
    
    def load_from_path(self, path: Path) -> Album:
        full_path = path.resolve()
        return Album(id = self.album_key(full_path),
                     name = full_path.name,
                     original_path = full_path,
                     generated_path = None,
                     thumbnail_path = None,
                     created = self.creation_timestamp_from_path(full_path))
        
    def build_album_tree(self) -> AlbumTree:
        # Starting point
        root_album = self.load_from_path(self.basepath)
        root_tree = AlbumTree(album=root_album, subalbums=[], images=[])
        
        # Use a queue to perform breadth-first search
        queue = deque([(self.basepath, root_tree)])
        
        while queue:
            current_path, current_tree = queue.popleft()
            
            # Iterate over all items in the current directory
            for item in current_path.iterdir():
                if item.is_dir():
                    # If it's a directory, create an album and add it to the subalbums
                    sub_album = self.load_from_path(item)
                    sub_tree = AlbumTree(album=sub_album, subalbums=[], images=[], parent=current_tree)
                    current_tree.subalbums.append(sub_tree)
                    queue.append((item, sub_tree))
                elif item.is_file() and path_is_image(item):
                    current_tree.imageCountEstimate += 1

        return root_tree
    
    
                     
    
    def creation_timestamp_from_path(self, path: Path) -> DateTime:
        # if the path name matches 'YYYY-MM-DD', then use that as the creation timestamp
        match = AlbumImport._date_regex.match(path.name)
        if match != None:
            year, month, day = match.groups()
            return pendulum.local(year=int(year), month=int(month), day=int(day), hour=0, minute=0, second=0)
        else:
            return pendulum.from_timestamp(path.stat().st_ctime)
    

# ---------------------------------------------------------------------------- #
#                              Album Service Class                             #
# ---------------------------------------------------------------------------- #

class AlbumService(DBService, AlbumImport, AlbumKeys):
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