NESTrisOCR
===
Simple OCR, captures subset of OBS window, then processes relevant numbers.
Forwards results via TCP.

Look at fastocr.py to see image processing, in particular brightness adjustment for red numbers.
Algorithm is simple KNearest (compare image to reference images, sum of difference of pixels)



Requirements
===
You need a working python installation to get everything running.

`python37-32` [Download here](https://www.python.org/downloads/release/python-372/)

When installing, make sure you `add to path` - this lets you run python from command prompt from any folder.

Next, [open a command window](https://www.google.com/search?q=how+to+open+a+command+prompt+windows). type in the following commands to install some modules required for this program

`pip install pillow`

`pip install pypiwin32`

You can verify they are installed by running python from the command prompt and then importing the modules
`python`

`import PIL` 

`import win32ui`


You shouldnt get any errors. Then, exit python
`exit()`

Running
===
`python screencap.py`

If you are not familiar with command prompt, [google it...](https://www.google.com/search?q=how+to+change+directory+in+command+prompt)

You'll want to open a command prompt, change to the directory of this repository, then run this python file.

Calibration
===
![calibration](https://github.com/alex-ong/NESTrisOCR/blob/master/example-calibration.png)

All calibration is in `calibration.py` and `screencap.py`

You need to set screencap.py to calibration mode, run it, and see what image it spits out.
I recommend just using `CALIBRATION = True` and `CALIBRATE_WINDOW = True`
It will spit out an image. Run the program repeatedly, tweaking the `calibration.py` until it looks right

**screencap.py**

Use the following to calibrate:
* `CALIBRATION` - turns calibration on. Program runs the following test images then exits.

* `CALIBRATE_WINDOW` - shows what you are capturing, overlaying the score,lines,level and stats

* `CALIBRATE_SCORE`  - shows captured image for score. Make sure it's pixel perfect!

* `CALIBRATE_LINES` - shows captured image for lines. Make sure it's pixel perfect!

* `CALIBRATE_LEVEL` - shows captured image for level. Make sure it's pixel perfect!

* `CALIBRATE_STATS` - shows captured image for stats. Make sure it's pixel perfect!

**calibration.py**

* `WINDOW_NAME` - the obs window name. it must start with these characters.

* `CAPTURE_COORDS` - pixel offset of window to capture. Start with (0,0, 200,200) and go from there...

* `_____Perc` - shouldn't need to adjust, but can slightly adjust to get pixel perfect, which will increase accuracy.

Testing
===
Uncomment `#print(message)` near the bottom of the file, and see what is being outputted. It should print out
the current lines, score, level.

`{'lines': '000', 'score', '000120', 'level', '00'}`


It will output via TCP to port 3338 by default.
