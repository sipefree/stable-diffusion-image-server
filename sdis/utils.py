import os
import sys
import argparse
import urllib.request
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from typing import Generator, List, Tuple
from PIL import Image
import piexif
import piexif.helper
import json
import re
from importlib import resources

from tqdm import tqdm


#-------------------------------------------------------------------------------
# General Utils
#-------------------------------------------------------------------------------


def chunks(iterable: List[str], chunk_size: int) -> Generator[List[str], None, None] :
    """Yield successive :attr:`chunk_size` sized chunks from :attr:`iterable`.

    :param iterable: an iterable to split into chunks.
    :param chunk_size: number of chunks to split :attr:`iterable` into.
    :return: a generator comtaining chunks of :attr:`iterable`.
    """
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i:i + chunk_size]


def rreplace(string: str, find: str, replace: str) -> str:
    """Starting from the right, replace the first occurence of
    :attr:`find` in :attr:`string` with :attr:`replace`.

    :param string: the string to search :attr:`find` in.
    :param find: the substring to find in :attr:`string`.
    :param replace: the substring to replace :attr:`find` with.
    :return: the replaced string.
    """
    return replace.join(string.rsplit(find, 1))


def urlify(slug: str, page=1) -> str:
    """Create a URL given a :attr:`slug` and a :attr:`page` index.

    :param slug: a slug from :func:`slugify`.
    :param page: an optional page number to include in the url.
    :return: the path of the HTML page described by :attr:`slug`.
    """
    if page > 1:
        url = f'{slug}/page/{page}/'
    else:
        url = f'{slug}/'
    return url


def filter_image(name: str) -> bool:
    """Checks if a given file name is an image.

    :param name: the file name to check.
    :return: ``True`` if the file name is an image, ``False`` otherwise.
    """
    _, ext = os.path.splitext(name)
    if ext.lower() in ['.jpeg', '.jpg', '.png', '.tiff']:
        return True
    return False


def find_thumb(album_path: str, image_root: str, thumb_dir: str) -> str:
    """Finds the first available image in a directory.

    :param album_path: the directory to scan.
    :param image_root: the path to thumbnails of images in :attr:`album_path`.
    :param thumb_dir: the path to the generated website.
    :return: relative path to an image in :attr:`album_path` if it
        exists, empty string otherwise.
    """
    image = ''
    for root, _, files in os.walk(album_path):
        for name in files:
            file_path = os.path.join(root, name)
            if filter_image(file_path):
                rel_path = os.path.relpath(file_path, album_path)
                image_path = os.path.join(image_root, rel_path)
                image = os.path.relpath(image_path, thumb_dir)
                return image
    return image

def scale_dims(width: int, height: int, min_val: int) -> Tuple[int, int]:
    """Scales :attr:`width` and :attr:`height` according to :attr:`min_val`.

    The smaller out of :attr:`width` and :attr:`height` is assigned a value of
    :attr:`min_val`, and the other parameter is scaled accordingly.

    :param width: the width to scale
    :param height: the height to scale
    :param min_val: the minimum value of width or height
    :return: a tuple containing the scaled width and height
    """
    if width < height:
        width = width * min_val / height
        height = min_val
    if width == height:
        width = min_val
        height = min_val
    if width > height:
        width = width * min_val / height
        height = min_val
    return round(width), round(height)


def album_sort_key(name: str) -> tuple[int, str]:
    special_keys = ['txt2img-images', 'img2img-images', 'txt2img-grids', 'img2img-grids', 'extras-images', 'init-images']
    if name in special_keys:
        return (0, special_keys.index(name))
    else:
        return (1, name)

def album_special_symbol(name: str) -> dict[str, str] | None:
    return {
        'txt2img-images': {
            'symbol': 'text_fields\u200Aarrow_right_alt\u200Aimage',
            'color': '#1E88E5AA'
        },
        'img2img-images': {
            'symbol': 'image\u200Aarrow_right_alt\u200Aimage',
            'color': '#00ACC1AA'
        },
        'txt2img-grids': {
            'symbol': 'text_fields\u200Aarrow_right_alt\u200Acalendar_view_month',
            'color': '#29B6F6AA'
        },
        'img2img-grids': {
            'symbol': 'image\u200Aarrow_right_alt\u200Acalendar_view_month',
            'color': '#4DD0E1AA'
        },
        'extras-images': {
            'symbol': 'resize',
            'color': '#5C6BC0AA'
        },
        'init-images': {
            'symbol': 'add_a_photo',
            'color': '#7E57C2AA'
        },
    }.get(name, None)


#-------------------------------------------------------------------------------
# Argparse Utils
#-------------------------------------------------------------------------------


def fixed_width_formatter(width: int=80) -> argparse.HelpFormatter:
    """Patch :class:`argparse.HelpFormatter` to use a fixed width.

    :param width: the maximum width of the help and usage text generated.
    :return: a patched instance of the formatter class.
    """

    class HelpFormatter(argparse.HelpFormatter):

        def __init__(self, *args, **kwargs):
            super().__init__(width=width, *args, **kwargs)

    return HelpFormatter


#-------------------------------------------------------------------------------
# Server Utils
#-------------------------------------------------------------------------------


class CustomHTTPHandler(SimpleHTTPRequestHandler):
    """An HTTP Handler to serve arbitrary directories compatible with Python 3.6.

    This handler uses :attr:`self.server.directory` instead of always using
    ``os.getcwd()``

    :meta private:
    """

    protocol_version = "HTTP/1.1"
    
    def __init__(self, *args, directory: str=os.getcwd(), no_cache_static=False, **kwargs):
        self.no_cache_static = no_cache_static
        self.static_path_prefix = os.path.join(directory, 'static')
        self.debug_path_prefix = str(resources.files("frontend") / "dist")
        SimpleHTTPRequestHandler.__init__(self, *args, directory=directory, **kwargs)

    def translate_path(self, path: str) -> str:
        """Translates a path to the local filename syntax."""
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        if hasattr(self.server, 'directory'):
            relpath = os.path.relpath(path, os.getcwd())
            path = os.path.join(self.server.directory, relpath)
        
        if self.no_cache_static and path.startswith(self.static_path_prefix):
            path = path.replace(self.static_path_prefix, self.debug_path_prefix)
        
        return path
    
    def log_message(self, format: str, *args: str) -> None:
        """A dummy function overridden to disable logging."""
        pass
    
    def end_headers(self) -> None:
        if self.no_cache_static and re.match('/static/.*', self.path):
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()
    
    def handle(self) -> None:
        """Handle multiple requests if necessary."""
        self.close_connection = True
        try:
            self.handle_one_request()
            while not self.close_connection:
                self.handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass


def start_server(args: argparse.Namespace) -> HTTPServer:
    """Start a Simple HTTP Server as a separate thread.
    
    :param args: preprocessed command line arguments.
    """
    # We need to create index.html for get_public_ip to receive HTTP 200.
    os.makedirs(args.thumb_dir, exist_ok=True)
    redir_html = os.path.join(args.thumb_dir, 'index.html')
    with open(redir_html, 'w') as f:
        f.write(f'<html><head><meta http-equiv="Refresh" '
                f'content="0; URL=html/"></head></html>')
    if sys.version_info.minor in [6, 7]:
        return start_server_36(args)
    if sys.version_info.minor >= 8:
        return start_server_38(args)


def get_public_ip(host: str, port: int) -> Tuple[str, int]:
    """Try to determine the public IP of the server.

    :param host: the fallback host to return in case of an error
    :param port: the port to check for public availability
    """
    try:
        with urllib.request.urlopen('https://api.ipify.org', timeout=5) as r:
            public_host = r.read().decode('utf-8')
            shis_server_url = f'http://{public_host}:{port}/'
        with urllib.request.urlopen(shis_server_url, timeout=5) as r:
            status = r.getcode()
        if status == 200:
            host = public_host
    except urllib.error.URLError:
        pass
    return host, port


def start_httpd(server: HTTPServer, address: Tuple[str, int], 
    handler: SimpleHTTPRequestHandler, args: argparse.Namespace) -> HTTPServer:
    """Try to start an HTTPServer, choosing the next available port.

    :param server: the server class to execute
    :param address: the address to start the server on
    :param handler: the request handler to use with the server
    :param args: preprocessed command line arguments
    """
    try:
        return server(address, handler)
    except OSError as error:
        if str(error) == '[Errno 98] Address already in use':
            if args.port is not None or address[1] > 7500:
                print(f'OSError: {error}. Try a different port using the -p flag.')
                sys.exit()
            else:
                address = (address[0], address[1]+1)
                return start_httpd(server, address, handler, args)
        else:
            raise error


def start_server_36(args):
    """Start an HTTP Server on Python 3.6 and Python 3.7.
    
    :meta private:
    """
    import socketserver

    class CustomHTTPServer(HTTPServer):
        def __init__(self, server_address: str, 
                     RequestHandlerClass: HTTPServer=CustomHTTPHandler,
                     directory: str=os.getcwd()):
            self.directory = directory
            HTTPServer.__init__(self, server_address, RequestHandlerClass)

    class ThreadingHTTPServer(socketserver.ThreadingMixIn, CustomHTTPServer):
        daemon_threads = False
    
    handler_class = CustomHTTPHandler
    server_class = partial(ThreadingHTTPServer, directory=args.thumb_dir)
    server_address = ("", args.port or 7447)
    httpd = start_httpd(server_class, server_address, handler_class, args)

    Thread(target=httpd.serve_forever).start()

    host, port = httpd.socket.getsockname()
    host, port = get_public_ip(host, port)
    serve_message = "Serving HTTP on {host}:{port}. "
    serve_message += "Press CTRL-C to quit."
    tqdm.write(serve_message.format(host=host, port=port))

    return httpd


def start_server_38(args):
    """Start an HTTP Server on Python 3.8 and above.
    
    :meta private:
    """    
    import contextlib
    from http.server import ThreadingHTTPServer, _get_best_family

    class DualStackServer(ThreadingHTTPServer):
        def server_bind(self):
            # suppress exception when protocol is IPv4
            with contextlib.suppress(Exception):
                self.socket.setsockopt(
                    socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            return super().server_bind()

    handler_class = partial(CustomHTTPHandler, directory=args.thumb_dir, no_cache_static=args.no_cache_static)
    server_class = DualStackServer
    server_class.address_family, server_address = \
        _get_best_family(None, args.port or 7447)
    httpd = start_httpd(server_class, server_address, handler_class, args)
    
    Thread(target=httpd.serve_forever).start()

    host, port = httpd.socket.getsockname()[:2]
    host, port = get_public_ip(host, port)
    tqdm.write(f"Serving HTTP on {host}:{port}. "
               f"Press CTRL-C to quit.")

    return httpd


#-------------------------------------------------------------------------------
# Image Info Utils
#-------------------------------------------------------------------------------

SD_IGNORED_INFO_KEYS = {
    'jfif', 'jfif_version', 'jfif_unit', 'jfif_density', 'dpi', 'exif',
    'loop', 'background', 'timestamp', 'duration', 'progressive', 'progression',
    'icc_profile', 'chromaticity', 'photoshop',
}

def read_info_from_image(image: Image.Image) -> tuple[str | None, dict]:
    items = (image.info or {}).copy()
    
    geninfo = items.pop('parameters', None)
    
    if "exif" in items:
        exif = piexif.load(items["exif"])
        exif_comment = (exif or {}).get("Exif", {}).get(piexif.ExifIFD.UserComment, b'')
        try:
            exif_comment = piexif.helper.UserComment.load(exif_comment)
        except ValueError:
            exif_comment = exif_comment.decode('utf8', errors="ignore")

        if exif_comment:
            items['exif comment'] = exif_comment
            geninfo = exif_comment
    
    for field in SD_IGNORED_INFO_KEYS:
        items.pop(field, None)

    return geninfo, items

def unquote(text):
    if len(text) == 0 or text[0] != '"' or text[-1] != '"':
        return text

    try:
        return json.loads(text)
    except Exception:
        return text

re_param_code = r'\s*([\w ]+):\s*("(?:\\"[^,]|\\"|\\|[^\"])+"|[^,]*)(?:,|$)'
re_param = re.compile(re_param_code)
re_imagesize = re.compile(r"^(\d+)x(\d+)$")

def parse_generation_parameters(x: str) -> dict[str, any]:
    """Parse a string of generation parameters into a dictionary.

    :param x: the string to parse.
    :return: a dictionary of parsed parameters.
    """
    res = {}

    prompt = ""
    negative_prompt = ""

    done_with_prompt = False

    *lines, lastline = x.strip().split("\n")
    if len(re_param.findall(lastline)) < 3:
        lines.append(lastline)
        lastline = ''

    for line in lines:
        line = line.strip()
        if line.startswith("Negative prompt:"):
            done_with_prompt = True
            line = line[16:].strip()
        if done_with_prompt:
            negative_prompt += ("" if negative_prompt == "" else "\n") + line
        else:
            prompt += ("" if prompt == "" else "\n") + line
            
    res["Prompt"] = prompt
    res["Negative prompt"] = negative_prompt

    for k, v in re_param.findall(lastline):
        try:
            if v[0] == '"' and v[-1] == '"':
                v = unquote(v)

            m = re_imagesize.match(v)
            if m is not None:
                res[f"{k}-1"] = m.group(1)
                res[f"{k}-2"] = m.group(2)
            else:
                res[k] = v
        except Exception:
            print(f"Error parsing \"{k}: {v}\"")
            
    # Missing CLIP skip means it was set to 1 (the default)
    if "Clip skip" not in res:
        res["Clip skip"] = "1"

    hypernet = res.get("Hypernet", None)
    if hypernet is not None:
        res["Prompt"] += f"""<hypernet:{hypernet}:{res.get("Hypernet strength", "1.0")}>"""
    
    return res