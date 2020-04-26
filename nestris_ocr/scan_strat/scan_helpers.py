from nestris_ocr.config import config
from nestris_ocr.utils import xywh_to_ltrb
from nestris_ocr.ocr_algo.digit import scoreImage as processDigits
from nestris_ocr.ocr_algo.board import parseImageSmart as processBoard
from nestris_ocr.ocr_algo.preview2 import parseImage as processPreview
from nestris_ocr.ocr_algo.piece_stats_spawn import parseImage as processSpawn

if config["performance.capture_method"] == "WINDOW_N_SLICE":
    from nestris_ocr.capturing.WindowAreasSlice import getWindowAreas
else:
    from nestris_ocr.capturing.WindowAreasDirect import getWindowAreas

PATTERNS = {
    "score": "ADDDDD",
    "lines": "DDD",
    "level": "AA",
    "stats": "DDD",
    "das": "BD",
}

# A few notes
# We always support scores past maxout
# We always support levels past 29

WINDOW_AREAS, FULL_RECT = getWindowAreas()


def mask_pattern(source, mask):
    result = ""
    for i, item in enumerate(source):
        if mask[i] == "X":
            result += "X"
        else:
            result += item
    return result


last_hwnd = None


def scan_full(full_image):
    if FULL_RECT:
        x, y, w, h = FULL_RECT
        return full_image.crop((x, y, x + w, y + h))

    return full_image


def get_sub_image(full_image, area):
    # conversion is needed: Image.crop expects ltrb, while WINDOW_AREAS has data in xywh
    return full_image.crop(xywh_to_ltrb(area))


def scan_text(full_image, pattern, digit_mask, window_area):
    mask = mask_pattern(pattern, digit_mask)
    sub_image = get_sub_image(full_image, window_area)
    return processDigits(sub_image, mask)


# scans the level image and returns a string
def scan_level(full_image):
    return scan_text(
        full_image, PATTERNS["level"], PATTERNS["level"], WINDOW_AREAS["level"]
    )


# scans the level image and returns a string. You can skip digits by inputting 'X' in the mask.
# "OOOXXX" means read first 3 digits
def scan_score(full_image, digit_mask="OOOOOO"):
    return scan_text(full_image, PATTERNS["score"], digit_mask, WINDOW_AREAS["score"])


def scan_lines(full_image, digit_mask="OOO"):
    return scan_text(full_image, PATTERNS["lines"], digit_mask, WINDOW_AREAS["lines"])


def scan_field(full_image, color1=None, color2=None):
    sub_image = get_sub_image(full_image, WINDOW_AREAS["field"])

    cached = True
    if color1 is None and color2 is None:
        color1 = get_sub_image(full_image, WINDOW_AREAS["color1"])
        color2 = get_sub_image(full_image, WINDOW_AREAS["color2"])
        cached = False
    return processBoard(sub_image, color1, color2, cached)


def scan_spawn(full_image):
    sub_image = get_sub_image(full_image, WINDOW_AREAS["stats2"])
    return processSpawn(sub_image)


def scan_stats_text(full_image):
    raise NotImplementedError


def scan_preview(full_image):
    sub_image = get_sub_image(full_image, WINDOW_AREAS["preview"])
    return processPreview(sub_image)
