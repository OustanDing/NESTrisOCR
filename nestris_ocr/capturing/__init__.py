import platform
import time

from nestris_ocr.config import config

capture_method = config["calibration.capture_method"]
if capture_method == "OPENCV":
    from nestris_ocr.capturing.opencv import OpenCVCapture as Capture
elif capture_method == "FILE":
    from nestris_ocr.capturing.file import FileCapture as Capture
elif capture_method == "WINDOW" and platform.system() == "Windows":
    from nestris_ocr.capturing.win32 import Win32Capture as Capture
else:
    raise ImportError("Invalid capture method")


capture = None


def init_capture(source_id, xywh_box):
    global capture

    capture = Capture(source_id, xywh_box)

    for i in range(5):
        try:
            _, image = capture.get_image()

            if image:
                print("Capture device ready!")
                break
        except Exception:
            print("Capture device not ready. {}...".format(i))
            time.sleep(1)
            continue
    else:
        print('Capture device cannot be found with "{}"'.format(source_id))


init_capture(config["calibration.source_id"], config["calibration.game_coords"])
