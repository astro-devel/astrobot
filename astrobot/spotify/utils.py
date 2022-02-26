import urllib.request
from colorthief import ColorThief


def get_dominant_color(url_path: str) -> int:
    """Get the dominant color of an image at a URL, and return the integer value of that color."""
    if not url_path:
        return 0
    path, res = urllib.request.urlretrieve(
        url_path, f"/tmp/{url_path.split('/')[-1]}.jpg"
    )
    hexvalue = ""
    rgbval = ColorThief(path).get_palette(quality=5)
    for i in rgbval[0]:
        hexvalue += hex(i).replace("0x", "")
    return int(hexvalue, 16)
