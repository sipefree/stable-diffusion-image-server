import pendulum
from pendulum.datetime import DateTime
import re
from collections import deque
from pathlib import Path
from typing import ClassVar, Optional
from .album import Album
from .album_keys import AlbumKeys
from ..images import Image, path_is_image


from attrs import define, field


@define
class AlbumTreeNode:
    album: Album                        = field()
    subalbums: list['AlbumTreeNode']    = field(factory=list)
    images: list[Image]                 = field(factory=list)
    parent: Optional['AlbumTreeNode']   = field(default=None)
    level: int                          = field(init=False)
    
    image_paths: list[Path]             = field(factory=list)
    deep_image_count: int               = field(default=0)
    
    def __attrs_post_init__(self):
        self.level = self.parent.level + 1 if self.parent != None else 0
    
@define
class AlbumTree:
    root: AlbumTreeNode                     = field()
    all_albums: list[AlbumTreeNode]         = field()
    albums_by_key: dict[str, AlbumTreeNode] = field(init=False)
    
    def __attrs_post_init__(self):
        self.albums_by_key = {album.album.id: album for album in self.all_albums}
        self._deep_count_images()
    
    def _deep_count_images(self):
        # non-recursive count of images in each album.
        # starts at the bottom of the tree and works its way up.
        sorted_trees = sorted(self.all_albums, key=lambda tree: tree.level, reverse=True)
        for tree in sorted_trees:
            child_image_count = sum(subtree.deep_image_count for subtree in tree.subalbums)
            tree.deep_image_count = len(tree.image_paths) + child_image_count



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
        root_tree = AlbumTreeNode(album=root_album)
        
        all_album_trees: list[AlbumTreeNode]  = [root_tree]

        # Use a queue to perform breadth-first search
        queue = deque([(self.basepath, root_tree)])

        while queue:
            current_path, current_tree = queue.popleft()

            # Iterate over all items in the current directory
            for item in current_path.iterdir():
                if item.is_dir():
                    # If it's a directory, create an album and add it to the subalbums
                    sub_album = self.load_from_path(item)
                    sub_tree = AlbumTreeNode(album=sub_album, parent=current_tree)
                    current_tree.subalbums.append(sub_tree)
                    queue.append((item, sub_tree))
                    all_album_trees.append(sub_tree)
                elif item.is_file() and path_is_image(item):
                    current_tree.image_paths.append(item)

        return AlbumTree(root_tree, all_album_trees)
    
    
    




    def creation_timestamp_from_path(self, path: Path) -> DateTime:
        # if the path name matches 'YYYY-MM-DD', then use that as the creation timestamp
        match = AlbumImport._date_regex.match(path.name)
        if match != None:
            year, month, day = match.groups()
            return pendulum.local(year=int(year), month=int(month), day=int(day), hour=0, minute=0, second=0)
        else:
            return pendulum.from_timestamp(path.stat().st_ctime)