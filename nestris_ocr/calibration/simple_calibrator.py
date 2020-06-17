from functools import partial
import tkinter as tk
import tkinter.ttk as ttk
import time

from PIL import Image

from nestris_ocr.calibration.string_chooser import StringChooser

from nestris_ocr.calibration.image_canvas import ImageCanvas
from nestris_ocr.calibration.draw_calibration import draw_calibration

from nestris_ocr.calibration.auto_calibrate import auto_calibrate_raw
from nestris_ocr.calibration.auto_number import auto_adjust_numrect
from nestris_ocr.calibration.capture_method import CaptureMethod

from nestris_ocr.calibration.state_vis import StateVisualizer
from nestris_ocr.calibration.widgets import Button
from nestris_ocr.capturing import uncached_capture, reinit_capture
from nestris_ocr.config import config

from nestris_ocr.scan_strat.naive_strategy import NaiveStrategy as Strategy

UPSCALE = 2
ENABLE_OTHER_OPTIONS = True

colorsImageSize = (80, 80)
blackWhiteImageSize = (80, 80)


class SimpleCalibrator(tk.Frame):
    def __init__(self, config):
        self.config = config
        root = tk.Tk()
        super().__init__(root)
        root.protocol("WM_DELETE_WINDOW", self.on_exit)
        root.focus_force()
        root.wm_title("NESTrisOCR calibrator")
        self.pack()
        self.root = root
        self.destroying = False
        root.config(background="black")
        self.strategy = Strategy()
        CaptureMethod(
            self,
            (config["capture.method"], config["capture.source_id"]),
            (
                self.gen_set_reload_capture("capture.method"),
                self.gen_set_reload_capture("capture.source_id"),
                partial(config.__setitem__, "capture.source_id"),
            ),
        ).grid(row=0, sticky="nsew")
        StringChooser(
            self,
            "player name",
            config["player.name"],
            partial(config.__setitem__, "player.name"),
            20,
        ).grid(row=1, sticky="nsew")

        # auto calibrate

        autoCalibrate = Button(
            self,
            text="Press this button when you're in game on \nLevel 00 with SCORE 000000 and LINES 000",
            command=self.autoDetectField,
            bg="red",
        )
        autoCalibrate.grid(row=2, columnspan=2)

        # webcam output
        f = tk.Frame(self)
        border = tk.Frame(f)
        border.grid(row=4, column=0, sticky="nsew")
        border.config(relief=tk.FLAT, bd=5, background="orange")
        self.boardImage = ImageCanvas(border, 512, 224 * 2)
        self.boardImage.pack()
        f.grid(row=3, column=0)

        # game output
        f = tk.Frame(self)
        self.stateVisualizer = StateVisualizer(f)
        self.stateVisualizer.pack()
        f.grid(row=3, column=1)
        self.progress_bar = ttk.Progressbar(
            self, orient=tk.HORIZONTAL, length=512, mode="determinate"
        )

        self.progress_bar["maximum"] = 100
        self.progress_bar.grid(row=5, columnspan=2, sticky="nsew")
        self.noBoard = True
        self.redrawImages()
        self.lastUpdate = time.time()

    def updateRedraw(self, func, result):
        func(result)
        self.redrawImages()

    def gen_set_reload_capture(self, key):
        def sub_function(result):
            config[key] = result
            reinit_capture()
            self.redrawImages()

        return sub_function

    def gen_set_config_and_redraw(self, key):
        def set_config_and_redraw(result):
            config[key] = result
            self.redrawImages()

        return set_config_and_redraw

    def update_game_coords(self, result):
        config["calibration.game_coords"] = result
        uncached_capture().xywh_box = result
        self.redrawImages()

    def update_graphics(self):
        # update raw board
        board = self.getNewBoardImage()
        print(board is None)
        if board is None:
            self.noBoard = True
            return
        else:
            self.noBoard = False
        self.boardImage.updateImage(board)

        # update stateVis
        ts, image = uncached_capture().get_image(rgb=True)
        self.strategy.update(ts, image)
        data = self.strategy.to_dict()
        self.stateVisualizer.updateValues(data)

    def redrawImages(self, event=None):
        self.lastUpdate = time.time()
        self.update_graphics()

    def autoLines(self):
        bestRect = auto_adjust_numrect(
            self.config["calibration.game_coords"],
            self.config["calibration.pct.lines"],
            3,
            self.update_progressbar,
        )
        if bestRect is not None:
            self.linesPerc.show(str(item) for item in bestRect)
            self.config["calibration.pct.lines"] = bestRect
        else:
            print("Please have score on screen as 000")

    def autoScore(self):
        bestRect = auto_adjust_numrect(
            self.config["calibration.game_coords"],
            self.config["calibration.pct.score"],
            6,
            self.update_progressbar,
        )
        if bestRect is not None:
            self.scorePerc.show(str(item) for item in bestRect)
            self.config["calibration.pct.score"] = bestRect
        else:
            print("Please have score on screen as 000000")

    def autoLevel(self):
        bestRect = auto_adjust_numrect(
            self.config["calibration.game_coords"],
            self.config["calibration.pct.level"],
            2,
            self.update_progressbar,
        )
        if bestRect is not None:
            self.levelPerc.show(str(item) for item in bestRect)
            self.config["calibration.pct.level"] = bestRect
        else:
            print("Please have score on screen as 00")

    def getNewBoardImage(self):
        return draw_calibration(self.config)

    def autoDetectField(self):
        rect = auto_calibrate_raw(self.config)
        if rect is not None:
            self.update_game_coords(rect)

    def update_progressbar(self, perc):
        self.progress_bar["value"] = round(perc * 100)
        self.progress_bar.update()

    def update(self):
        if not self.destroying:
            self.redrawImages()
            super().update()

    def on_exit(self):
        self.destroying = True
        self.root.destroy()


# sources: PixelDimensions (w,h), RectPerc(x,y,w,h)
# out: RectPixel(x,y,x2,y2)
def pixelPercRect(dim, rectPerc):
    x1 = round(dim[0] * rectPerc[0])
    y1 = round(dim[1] * rectPerc[1])
    x2 = round(x1 + dim[0] * rectPerc[2])
    y2 = round(y1 + dim[1] * rectPerc[3])
    return x1, y1, x2, y2


ASSET_ROOT = "nestris_ocr/assets/"


def LoadSamplePreview():
    im = Image.open(ASSET_ROOT + "sprite_templates/preview-reference.png")
    return im


def LoadSamplePreview2():
    im = Image.open(ASSET_ROOT + "sprite_templates/preview-reference-border.png")
    return im
