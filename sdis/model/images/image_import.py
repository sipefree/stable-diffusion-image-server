from pathlib import Path
from attrs import define, field

from .image_keys import ImageKeys
from .image import Image
from collections.abc import AsyncIterator
from ..async_overlay import AsyncProcessMap

@define(frozen=True)
class ImageImportJob:
    basepath: Path      = field()
    genpath: Path       = field()
    image_path: Path    = field()
    album_key: str      = field()

@define(frozen=True)
class ImageImportResult:
    image: Image
    album_key: str


class ImageImport(ImageKeys):
    
    def __init__(self, basepath: Path, genpath: Path):
        self.genpath = genpath
        super().__init__(basepath)
        
    def import_image(self, image_path: Path, album_key: str) -> ImageImportResult:
        pass
    
    @classmethod
    def import_images_async(cls,
                            jobs: list[ImageImportJob],
                            max_workers: int = 8,
                            tqdm_unit: str = 'raster',
                            tqdm_desc: str = 'Importing images',
                            tqdm_dynamic_ncols: bool = True,
                            tqdm_leave: bool = True) -> AsyncIterator[ImageImportResult]:
        return AsyncProcessMap(
            func = _task_import_image, 
            input = jobs,
            max_workers = max_workers,
            unit = tqdm_unit,
            desc = tqdm_desc,
            dynamic_ncols = tqdm_dynamic_ncols,
            leave = tqdm_leave
        )

def _task_import_image(job: ImageImportJob) -> ImageImportResult:
    importer = ImageImport(
        basepath = job.basepath,
        genpath = job.genpath
    )
    return importer.import_image(job.image_path, job.album_key)

# ---------------------------------------------------------------------------- #
#                                   Utilities                                  #
# ---------------------------------------------------------------------------- #

def path_is_image(path: Path) -> bool:
    """Returns True if the given path is an image file."""
    return path.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.tiff', '.webp')