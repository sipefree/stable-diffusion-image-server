import pytest
from sdis.model.album import AlbumKeys, Album
from pathlib import Path
import pendulum

@pytest.fixture
def base_path() -> Path:
    return Path("/some/base/path")

@pytest.fixture
def gen_path() -> Path:
    return Path("/some/gen/path")

@pytest.fixture
def album_keys(base_path: Path) -> AlbumKeys:
    return AlbumKeys(basepath=base_path)

@pytest.fixture
def album_1(base_path: Path, gen_path: Path) -> Album:
    return Album(id="album:album_1",
                 name="album_1",
                 original_path=(base_path / "album_1"),
                 generated_path=(gen_path / "html" / "album_1"),
                 thumbnail_path=(gen_path / "album_thumbnails" / "album_1" / "thumbnail.png"),
                 created=pendulum.local(2023, 6, 1))
                 

def test_album_key_with_album_object(album_keys: AlbumKeys, album_1: Album):
    expected_key = "album:album_1"
    assert album_keys.album_key(album_1) == expected_key

def test_album_key_with_path_object(album_keys: AlbumKeys):
    album_path = Path("/some/base/path/test_album")
    expected_key = "album:test_album"
    assert album_keys.album_key(album_path) == expected_key

def test_album_key_with_str_object(album_keys: AlbumKeys):
    album_str = "album:test_album"
    expected_key = "album:test_album"
    assert album_keys.album_key(album_str) == expected_key
    
def test_resolve_stem_with_album(album_keys: AlbumKeys, album_1: Album):
    expected_stem = "album_1"
    assert album_keys.resolve_stem(album_1) == expected_stem
    assert album_keys.album_key(album_1) == f"album:{expected_stem}"
    assert album_keys.subalbums_key(album_1) == f"album_subalbums:{expected_stem}"
    assert album_keys.images_key(album_1) == f"album_images:{expected_stem}"

def test_resolve_stem_with_path(album_keys: AlbumKeys):
    album_path = Path("/some/base/path/test_album2")
    expected_stem = "test_album2"
    assert album_keys.resolve_stem(album_path) == expected_stem
    assert album_keys.album_key(album_path) == f"album:{expected_stem}"
    assert album_keys.subalbums_key(album_path) == f"album_subalbums:{expected_stem}"
    assert album_keys.images_key(album_path) == f"album_images:{expected_stem}"

def test_resolve_stem_with_key_str(album_keys: AlbumKeys):
    album_str = "album:test_album3"
    expected_stem = "test_album3"
    assert album_keys.resolve_stem(album_str) == expected_stem
    assert album_keys.album_key(album_str) == f"album:{expected_stem}"
    assert album_keys.subalbums_key(album_str) == f"album_subalbums:{expected_stem}"
    assert album_keys.images_key(album_str) == f"album_images:{expected_stem}"

def test_resolve_stem_with_regular_str(album_keys: AlbumKeys):
    album_str = "/some/base/path/test_album4"
    expected_stem = "test_album4"
    assert album_keys.resolve_stem(album_str) == expected_stem
    assert album_keys.album_key(album_str) == f"album:{expected_stem}"
    assert album_keys.subalbums_key(album_str) == f"album_subalbums:{expected_stem}"
    assert album_keys.images_key(album_str) == f"album_images:{expected_stem}"

def test_resolve_stem_with_encoded_str(album_keys: AlbumKeys):
    album_str = "test%3Aalbum5"
    expected_stem = "test%3Aalbum5"
    assert album_keys.resolve_stem(album_str) == expected_stem
    assert album_keys.album_key(album_str) == f"album:{expected_stem}"
    assert album_keys.subalbums_key(album_str) == f"album_subalbums:{expected_stem}"
    assert album_keys.images_key(album_str) == f"album_images:{expected_stem}"

def test_resolve_stem_invalid_type(album_keys: AlbumKeys):
    # passing an integer to cause a ValueError
    match = "Must pass either Album, Path, or str."
    with pytest.raises(ValueError, match=match):
        album_keys.resolve_stem(123) # type: ignore 
    with pytest.raises(ValueError, match=match):
        album_keys.album_key(123) # type: ignore 
    with pytest.raises(ValueError, match=match):
        album_keys.subalbums_key(123) # type: ignore 
    with pytest.raises(ValueError, match=match):
        album_keys.images_key(123) # type: ignore 

def test_subalbums_key(album_keys: AlbumKeys):
    album_str = "album:test_album6"
    expected_key = "album_subalbums:test_album6"
    assert album_keys.subalbums_key(album_str) == expected_key

def test_images_key(album_keys: AlbumKeys):
    album_str = "album:test_album7"
    expected_key = "album_images:test_album7"
    assert album_keys.images_key(album_str) == expected_key

