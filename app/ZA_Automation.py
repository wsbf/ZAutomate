#!/usr/bin/env python

import Tkinter
from Tkinter import Label, StringVar, Button, Frame, Scrollbar, Listbox
from ZAutomate_CartQueue import CartQueue

COLOR_BUTTON_STOPPED = "#008500"
COLOR_BUTTON_PLAYING = "#FFFF00"
COLOR_BUTTON_STOPPING = "#FF0000"

FONT_TITLE = ('Helvetica', 36, 'bold italic')
FONT = ('Helvetica', 12, 'bold')

TEXT_TITLE = "ZAutomate :: Automation"
TEXT_BUTTON_STOPPED = "START"
TEXT_BUTTON_PLAYING = "STOP"
TEXT_BUTTON_STOPPING = "STOP NOW"
TEXT_PLAYLIST_TIME = "Start Time"
TEXT_PLAYLIST_TRACK = "Track"
TEXT_PLAYLIST_ARTIST = "Artist"

class Automation(Frame):
    STATE_STOPPED = 1
    STATE_PLAYING = 2
    STATE_STOPPING = 3

    _state = None
    _cart_queue = None

    _button_text = None
    _button = None

    _list_time = None
    _list_track = None
    _list_artist = None

    def __init__(self):
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

        self._cart_queue = CartQueue(self.master, self._update_ui)
        self._cart_queue.add_tracks()
        self._update_ui()

    ###YATES_COMMENT: Event Handler for scrolling through the three Windows.
    def _scroll_playlist(self, *args):
        self._list_time.yview(*args)
        self._list_track.yview(*args)
        self._list_artist.yview(*args)

    ###YATES_COMMENT: Event Handler for Start->Stopping->Stopped state machine
    def _update_state(self):
        if self._state is self.STATE_STOPPED:
            self.start()
        elif self._state is self.STATE_PLAYING:
            self.stop_soft()
        elif self._state is self.STATE_STOPPING:
            self.stop_hard()

    def start(self):
        print "Starting Automation..."
        self._cart_queue.start(True)
        self._state = self.STATE_PLAYING
        self._button_text.set(TEXT_BUTTON_PLAYING)
        self._button.config(bg=COLOR_BUTTON_PLAYING, highlightbackground=COLOR_BUTTON_PLAYING)

    def stop_soft(self):
        print "Stopping Automation after this track..."
        self._cart_queue.stop_soft()
        self._state = self.STATE_STOPPING
        self._button_text.set(TEXT_BUTTON_STOPPING)
        self._button.config(bg=COLOR_BUTTON_STOPPING, highlightbackground=COLOR_BUTTON_STOPPING)

    def stop_hard(self):
        print "Stopping Automation immediately."
        self._cart_queue.transition()
        self._state = self.STATE_STOPPED
        self._button_text.set(TEXT_BUTTON_STOPPED)
        self._button.config(bg=COLOR_BUTTON_STOPPED, highlightbackground=COLOR_BUTTON_STOPPED)

    # callback: when anything happens in _cart_queue, run this to update the UI's state
    def _update_ui(self):
        # clear and reset the playlist
        self._list_time.delete(0, Tkinter.END)
        self._list_track.delete(0, Tkinter.END)
        self._list_artist.delete(0, Tkinter.END)

        for cart in self._cart_queue.get_queue():
            self._list_time.insert(Tkinter.END, cart.GetFmtStartTime())
            self._list_track.insert(Tkinter.END, cart.title)
            self._list_artist.insert(Tkinter.END, cart.issuer)

        # HACK: update the button state if a soft stop occured
        if self._state is self.STATE_STOPPING:
            self._state = self.STATE_STOPPED
            self._button_text.set(TEXT_BUTTON_STOPPED)
            self._button.config(bg=COLOR_BUTTON_STOPPED, highlightbackground=COLOR_BUTTON_STOPPED)

    def destroy(self):
        self._cart_queue.save()

automation = Automation()
automation.master.protocol("WM_DELETE_WINDOW", automation.master.destroy)
automation.master.title(TEXT_TITLE)
automation.master.mainloop()
