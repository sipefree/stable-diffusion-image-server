# ---------------------------------------------------------------------------- #
#                               Album Tree Class                               #
# ---------------------------------------------------------------------------- #

import pendulum
from pendulum.datetime import DateTime
import re
from collections import deque
from pathlib import Path
from typing import ClassVar
from .album import Album
from .album_keys import AlbumKeys
from sdis.model.image import Image, path_is_image


from attrs import define, field


@define
class AlbumTree:
    album: Album                    = field()
    subalbums: list['AlbumTree']    = field(factory=list)
    images: list[Image]             = field(factory=list)
    imageCountEstimate: int         = field(default=0)
    subCountEstimate: int           = field(default=0)
    parent: 'AlbumTree'             = field(default=None)




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