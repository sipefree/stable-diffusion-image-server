from pathlib import Path


class ImageImport:
    pass

# ---------------------------------------------------------------------------- #
#                                   Utilities                                  #
# ---------------------------------------------------------------------------- #

def path_is_image(path: Path) -> bool:
    """Returns True if the given path is an image file."""
    return path.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.tiff', '.webp')