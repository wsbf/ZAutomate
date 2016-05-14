#!/usr/bin/env python

"""The Automation module provides a GUI for radio automation."""
import Tkinter
from Tkinter import Label, StringVar, Button, Frame, Scrollbar, Listbox
from cartqueue import CartQueue
from meter import Meter

METER_WIDTH = 800

COLOR_BUTTON_STOPPED = "#008500"
COLOR_BUTTON_PLAYING = "#FFFF00"
COLOR_BUTTON_STOPPING = "#FF0000"

FONT_TITLE = ("Helvetica", 36, "bold italic")
FONT = ("Helvetica", 12, "bold")

TEXT_TITLE = "ZAutomate :: Automation"
TEXT_BUTTON_STOPPED = "START"
TEXT_BUTTON_PLAYING = "STOP"
TEXT_BUTTON_STOPPING = "STOP NOW"
TEXT_PLAYLIST_TIME = "Start Time"
TEXT_PLAYLIST_TRACK = "Track"
TEXT_PLAYLIST_ARTIST = "Artist"

class Automation(Frame):
    """The Automation class is a GUI that provides radio automation."""
    STATE_STOPPED = 1
    STATE_PLAYING = 2
    STATE_STOPPING = 3

    _state = None
    _button_text = None
    _button = None

    _meter = None
    _cart_queue = None

    _list_time = None
    _list_track = None
    _list_artist = None

    def __init__(self):
        """Construct an Automation window."""
        Frame.__init__(self)

        # initialize title
        title = Label(self.master, fg='#000', font=FONT_TITLE, text=TEXT_TITLE)
        title.grid(row=0, column=0, columnspan=3)

        # initialize button and state
        self._state = self.STATE_STOPPED

        self._button_text = StringVar()
        self._button_text.set(TEXT_BUTTON_STOPPED)

        self._button = Button(self.master, textvariable=self._button_text, command=self._update_state, width=16, height=2)
        self._button.config(bd=2, bg=COLOR_BUTTON_STOPPED, highlightbackground=COLOR_BUTTON_STOPPED)
        self._button.grid(row=0, column=3)

        # initialize the meter
        self._meter = Meter(self.master, METER_WIDTH, self._get_meter_data)
        self._meter.grid(row=1, column=0, columnspan=4)

        # initialize playlist view
        playlist = Frame(self.master, bd=2, relief=Tkinter.SUNKEN)
        Label(playlist, font=FONT, anchor=Tkinter.CENTER, width=16, text=TEXT_PLAYLIST_TIME).grid(row=0, column=0)
        Label(playlist, font=FONT, anchor=Tkinter.CENTER, width=32, text=TEXT_PLAYLIST_TRACK).grid(row=0, column=1)
        Label(playlist, font=FONT, anchor=Tkinter.CENTER, width=32, text=TEXT_PLAYLIST_ARTIST).grid(row=0, column=2)

        inner_playlist = Frame(playlist)
        scroll = Scrollbar(inner_playlist, orient="vertical", command=self._scroll_playlist)
        self._list_time = Listbox(inner_playlist, selectmode='single', yscrollcommand=scroll.set, exportselection=0, width=16, height=20)
        self._list_track = Listbox(inner_playlist, selectmode='single', yscrollcommand=scroll.set, exportselection=0, width=32, height=20)
        self._list_artist = Listbox(inner_playlist, selectmode='single', yscrollcommand=scroll.set, exportselection=0, width=32, height=20)

        scroll.pack(side="right", fill="y")
        self._list_time.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        self._list_track.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        self._list_artist.pack(side="left", fill="x", expand=True, padx=2, pady=2)

        inner_playlist.grid(row=1, column=0, columnspan=3)
        playlist.grid(row=4, column=0, columnspan=4)

        # initialize cart queue
        self._cart_queue = CartQueue(self._cart_start, self._cart_stop, self._update_ui)
        self._cart_queue.add_tracks()
        self._update_ui()

        # begin the event loop
        self.master.protocol("WM_DELETE_WINDOW", self.master.destroy)
        self.master.title(TEXT_TITLE)
        self.master.mainloop()

    def _scroll_playlist(self, *args):
        """Scroll the playlist view.

        :param args
        """
        self._list_time.yview(*args)
        self._list_track.yview(*args)
        self._list_artist.yview(*args)

    def _update_state(self):
        """Move Automation to the next state.

        The state machine is as follows:
        STATE_STOPPED -> STATE_PLAYING -> STATE_STOPPING -> STATE_STOPPED
        """
        if self._state is self.STATE_STOPPED:
            self.start()
        elif self._state is self.STATE_PLAYING:
            self.stop_soft()
        elif self._state is self.STATE_STOPPING:
            self.stop_hard()

    def start(self):
        """Start Automation."""
        print "Starting Automation..."
        self._cart_queue.start()
        self._state = self.STATE_PLAYING
        self._button_text.set(TEXT_BUTTON_PLAYING)
        self._button.config(bg=COLOR_BUTTON_PLAYING, highlightbackground=COLOR_BUTTON_PLAYING)

    def stop_soft(self):
        """Stop Automation at the end of the current track."""
        print "Stopping Automation after this track..."
        self._cart_queue.stop_soft()
        self._state = self.STATE_STOPPING
        self._button_text.set(TEXT_BUTTON_STOPPING)
        self._button.config(bg=COLOR_BUTTON_STOPPING, highlightbackground=COLOR_BUTTON_STOPPING)

    def stop_hard(self):
        """Stop Automation immediately."""
        print "Stopping Automation immediately."
        self._cart_queue.transition()
        self._state = self.STATE_STOPPED
        self._button_text.set(TEXT_BUTTON_STOPPED)
        self._button.config(bg=COLOR_BUTTON_STOPPED, highlightbackground=COLOR_BUTTON_STOPPED)

    def _cart_start(self):
        """Start the meter when a cart starts."""
        self._meter.start()

    def _cart_stop(self):
        """Reset the meter when a cart stops."""
        self._meter.reset()

    def _update_ui(self):
        """Update the user interface.

        This function is called when the cart queue is updated.
        """

        # clear and reset the playlist
        self._list_time.delete(0, Tkinter.END)
        self._list_track.delete(0, Tkinter.END)
        self._list_artist.delete(0, Tkinter.END)

        for cart in self._cart_queue.get_queue():
            self._list_time.insert(Tkinter.END, cart.start_time.strftime("%I:%M:%S %p"))
            self._list_track.insert(Tkinter.END, cart.title)
            self._list_artist.insert(Tkinter.END, cart.issuer)

        # HACK: update the button state if a soft stop occured
        if self._state is self.STATE_STOPPING:
            self._state = self.STATE_STOPPED
            self._button_text.set(TEXT_BUTTON_STOPPED)
            self._button.config(bg=COLOR_BUTTON_STOPPED, highlightbackground=COLOR_BUTTON_STOPPED)

    def _get_meter_data(self):
        """Get meter data for the first track in the queue."""
        queue = self._cart_queue.get_queue()

        if len(queue) > 0:
            return queue[0].get_meter_data()
        else:
            return None

    def destroy(self):
        """Destroy the Automation window."""
        self._cart_queue.save()

Automation()
