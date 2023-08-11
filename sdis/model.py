from attrs import define, field

@define
class Album:
    id: int = field(default=None)  # Autoincrement, so default is None
    name: str = field()
    parent_id: int = field(default=None)  # Nullable, so default is None
    thumbnail_path: str = field()
    creation_timestamp: str = field(default=None)  # Auto set, so default is None

@define
class Image:
    id: int = field(default=None)  # Autoincrement, so default is None
    album_id: int = field()
    original_path: str = field()
    fullsize_thumbnail_path: str = field(default=None)
    large_thumbnail_path: str = field(default=None)
    small_thumbnail_path: str = field(default=None)
    width: int = field()
    height: int = field()
    creation_timestamp: str = field(default=None)  # Auto set, so default is None
    parameters_text: str = field()
    parameters_json: str = field()
