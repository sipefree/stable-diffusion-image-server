import pytest
from sdis.model.service import DBBase, DBService
from pathlib import Path

@pytest.fixture
def base_path() -> Path:
    return Path("/some/base/path")

@pytest.fixture
def base_instance(base_path: Path) -> DBBase:
    return DBBase(basepath=base_path)

def test_base(base_path: Path, base_instance: DBBase):
    assert base_instance.basepath == base_path

def test_pathstem(base_path: Path, base_instance: DBBase):
    full_path = Path("/some/base/path/test_album")
    expected_pathstem = "test_album"
    assert base_instance.pathstem(full_path) == expected_pathstem
    
def test_quotepath(base_instance: DBBase):
    # Test paths that need quoting
    assert base_instance.quotepath("some/path:with:colons") == "some/path%3Awith%3Acolons"
    assert base_instance.quotepath("path/with special&characters") == "path/with special%26characters"
    
    # Test paths that don't need quoting
    assert base_instance.quotepath("some/normal/path") == "some/normal/path"
    assert base_instance.quotepath("path with spaces") == "path with spaces"

def test_unquotepath(base_instance: DBBase):
    # Test paths that were quoted
    assert base_instance.unquotepath("some/path%3Awith%3Acolons") == "some/path:with:colons"
    assert base_instance.unquotepath("path/with%20special%26characters") == "path/with special&characters"
    assert base_instance.unquotepath("path/with special%26characters") == "path/with special&characters"
    
    # Test paths that were not quoted
    assert base_instance.unquotepath("some/normal/path") == "some/normal/path"
    assert base_instance.unquotepath("path with spaces") == "path with spaces"

def test_pathstem_special_characters(base_path: Path, base_instance: DBBase):
    # Test paths with colons
    full_path = base_path / "some:path:with:colons"
    expected_pathstem = "some%3Apath%3Awith%3Acolons"
    assert base_instance.pathstem(full_path) == expected_pathstem

    # Test paths with spaces and other special characters
    full_path = base_path / "path with spaces & other characters"
    expected_pathstem = "path with spaces %26 other characters"
    assert base_instance.pathstem(full_path) == expected_pathstem

    # Test paths with multiple levels
    full_path = base_path / "level1" / "level2:with:colons"
    expected_pathstem = "level1/level2%3Awith%3Acolons"
    assert base_instance.pathstem(full_path) == expected_pathstem
