from pathlib import Path
from .service import DBBase, DBService
from .image import Image, ImageService
from .album import Album, AlbumService

class ImportService(DBService):
    
    def __init__(self, image_service: ImageService, album_service: AlbumService):
        conn = image_service.conn
        app = image_service.app
        assert(image_service.app == album_service.app)
        assert(image_service.conn == album_service.conn)
        super().__init__(conn, app)