﻿import tkinter as tk
from PIL import Image, ImageDraw
from lib import *

class Calibrator(tk.Frame):
            
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
        label = tk.Label(self, text="test")
        label.pack()
    
    def update(self):        
        if not self.destroying:
            super().update()
    
    def on_exit(self):        
        self.destroying = True
        self.root.destroy()



def highlight_calibration(img, config):    
    poly = Image.new('RGBA', (img.width,img.height))
    draw = ImageDraw.Draw(poly)
    
    red = (255,0,0,128)    
    blue = (0,0,255,128)       
    orange = (255,165,0,128)
    
    scorePerc, linesPerc, levelPerc = (config.scorePerc, config.linesPerc, config.levelPerc)
    #score
    draw.rectangle(screenPercToPixels(img.width,img.height,scorePerc),fill=red)
    #lines
    draw.rectangle(screenPercToPixels(img.width,img.height,linesPerc),fill=red)
    #level
    draw.rectangle(screenPercToPixels(img.width,img.height,levelPerc),fill=red)    
    if config.capture_stats:
        if config.stats_method == 'TEXT':
            #pieces
            draw.rectangle(screenPercToPixels(img.width,img.height,statsPerc),fill=blue)
            for value in generate_stats(config.CAPTURE_COORDS,statsPerc,scorePerc[3],False).values():
                draw.rectangle(screenPercToPixels(img.width,img.height,value),fill=orange)
        else: #config.stats_method == 'FIELD':
            stats2Perc = config.stats2Perc
            draw.rectangle(screenPercToPixels(img.width,img.height,stats2Perc),fill=blue)
            for x in range(4):
                for y in range(2):                
                    blockPercX = lerp(stats2Perc[0], stats2Perc[0] + stats2Perc[2], x / 4.0 + 1 / 8.0)
                    blockPercY = lerp(stats2Perc[1], stats2Perc[1] + stats2Perc[3], y / 2.0 + 1 / 4.0)
                    rect = (blockPercX - 0.01, blockPercY - 0.01, 0.02, 0.02)
                    draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=red)
        
        img.paste(poly,mask=poly)    
    del draw

#todo, return image or array of images with cropped out sections.    
def draw_calibration(config):
    hwnd = getWindow()
    if hwnd is None:
        print("Unable to find window with title:",  config.WINDOW_NAME)
        return
    
    img = WindowCapture.ImageCapture(config.CAPTURE_COORDS, hwnd)
    highlight_calibration(img, config)    
    return img
    