import thread
import time
from Tkinter import Canvas

# METER_WIDTH = 0
METER_HEIGHT = 135
METER_INTERVAL = 0.25

COLOR_METER_BG = "#000000"
COLOR_METER_TEXT = "#33CCCC"

FONT_HEAD = ("Helvetica", 22, "bold")
FONT_SMALL = ("Helvetica", 12)
FONT_NUM = ("Courier", 22, "bold")

class Meter(Canvas):
    _data_callback = None  # called on every "tick" of the Meter to get the next value
    _end_callback = None   # called when the Meter reaches (about) 100%
    _is_playing = False

    _position = None
    _length = None
    _cue = None
    _title = None
    _artist = None

    def __init__(self, master, width, data_callback, end_callback):
        Canvas.__init__(self, master, bg=COLOR_METER_BG, borderwidth="2", relief="groove", width=width, height=METER_HEIGHT)

        self._data_callback = data_callback
        self._end_callback = end_callback

        self._width = (int)(self.cget("width"))
        self._x0 = 0
        self._y0 = METER_HEIGHT - 25
        self._x1 = self._width + 5
        self._y1 = METER_HEIGHT

        self.create_text(10, 60, anchor="w", font=FONT_SMALL, text="Position", fill=COLOR_METER_TEXT)
        self.create_text(140, 60, anchor="w", font=FONT_SMALL, text="Length", fill=COLOR_METER_TEXT)
        self.create_text(270, 60, anchor="w", font=FONT_SMALL, text="To Cue", fill=COLOR_METER_TEXT)

        self._position = self.create_text(10, 85, anchor="w", font=FONT_NUM, text="0:00", fill=COLOR_METER_TEXT)
        self._length = self.create_text(140, 85, anchor="w", font=FONT_NUM, text="0:00", fill=COLOR_METER_TEXT)
        self._cue = self.create_text(270, 85, anchor="w", font=FONT_NUM, text="0:00", fill=COLOR_METER_TEXT)
        self._title = self.create_text(10, 20, anchor="w", font=FONT_HEAD, text="--", fill=COLOR_METER_TEXT)
        self._artist = self.create_text(self._width, 20, anchor="e", font=FONT_HEAD, text="--", fill=COLOR_METER_TEXT)

        # x0 y0 x1 y1
        self._bar_bg = self.create_rectangle(self._x0, self._y0, self._x1, self._y1, fill="#008500", width=1)
        self._bar_fg = self.create_rectangle(self._x0, self._y0, 0, self._y1, fill="#FF0000", width=1)

    ## convert 180 seconds into 3:00
    def _get_fmt_time(self, seconds):
        return time.strftime("%M:%S", time.localtime(seconds))

    def _run(self):
        while self._is_playing is True:
            # (position [ms], length [ms], title, artist, id, type)
            data = self._data_callback()

            # if data[0] >= data[1]:
            #     break

            if data[1] is not 0:
                value = (float)(data[0]) / (float)(data[1])
            else:
                value = 0.0

            position = (int)(data[0]) / 1000
            length = (int)(data[1]) / 1000
            cue = length - position
            title = data[2]
            artist = data[3]

            self.itemconfigure(self._position, text=self._get_fmt_time(position))
            self.itemconfigure(self._length, text=self._get_fmt_time(length))
            self.itemconfigure(self._cue, text=self._get_fmt_time(cue))
            self.itemconfigure(self._title, text=title)
            self.itemconfigure(self._artist, text=artist)
            self.coords(self._bar_fg, self._x0, self._y0, int(self._width * value), self._y1)

            time.sleep(METER_INTERVAL)

        # if self._end_callback is not None:
        #     self._end_callback()

    def start(self):
        self._is_playing = True
        thread.start_new_thread(self._run, ())

    def reset(self):
        self._is_playing = False
        self.itemconfigure(self._position, text=self._get_fmt_time(0))
        self.itemconfigure(self._length, text=self._get_fmt_time(0))
        self.itemconfigure(self._cue, text=self._get_fmt_time(0))
        self.itemconfigure(self._title, text="--")
        self.itemconfigure(self._artist, text="--")
        self.coords(self._bar_fg, 0, self._y0, 0, self._y1)
