﻿import tkinter as tk
import multiprocessing
from calibration.OptionChooser import OptionChooser
from calibration.BoolChooser import BoolChooser
INSTANCE = None
 
class OtherOptions(tk.Toplevel):
    def __init__(self, root, config, on_destroy):
        super().__init__(root)
        self.config = config
        self.on_destroy = on_destroy
        #multiprocessing
        items = [i + 1 for i in range(multiprocessing.cpu_count())]
        itemsStr = [str(item) for item in items]        
        mt = OptionChooser(self,'Use multi_thread', items, itemsStr, 
                           config.threads, self.changeMultiThread).pack(fill='both')        
        #hexSupport
        BoolChooser(self,'Support hex scores (scores past 999999 as A00000 to F99999)',
                    config.hexSupport,self.changeHexSupport).pack(fill='both')
        #captureField
        BoolChooser(self,'Capture game field',
                    config.capture_field,self.changeCaptureField).pack(fill='both')

        #captureStats
        BoolChooser(self,'Capture Piece Stats', config.capture_stats, 
                    self.changeCaptureStats).pack(fill='both')

        self.statsMethod = OptionChooser(self,'Piece Stats capture method',
                                         ['TEXT','FIELD'],['TEXT','FIELD'],
                                         config.stats_method,self.changeStatsMethod)
        if config.capture_stats:
            self.statsMethod.pack(fill='both')

        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.wm_title("NESTrisOCR Options")
        self.grab_set()

    def changeMultiThread(self, value):
        self.config.setThreads(value)
    
    def changeHexSupport(self, value):        
        self.config.setHexSupport(value)
    
    def changeCaptureField(self, value):        
        self.config.setCaptureField(value)

    def changeCaptureStats(self,value):
        self.config.setCaptureStats(value)
        if value:
            self.statsMethod.pack(fill='both')
        else:
            self.statsMethod.pack_forget()
    
    def changeStatsMethod(self, value):
        self.config.setStatsMethod(value)

    def on_exit(self):        
        global INSTANCE
        INSTANCE = None
        self.on_destroy()
        self.destroy()

def create_window(root, config, on_destroy):
    global INSTANCE
    if INSTANCE is None:    
        INSTANCE = OtherOptions(root,config,on_destroy)
    
