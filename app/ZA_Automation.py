#!/usr/bin/env python

from Tkinter import Tk, Label, StringVar, Button, Frame, SUNKEN, CENTER, Scrollbar, Listbox, END
from ZAutomate_CartQueue import CartQueue

SIZE_X = 800
SIZE_Y = 600
OFFSET_X = 0
OFFSET_Y = 0
WINDOW_PARAMS = (str)(SIZE_X) + "x" + (str)(SIZE_Y) \
        + "+" + (str)(OFFSET_X) + "+" + (str)(OFFSET_Y)

class Automation():
    Master = None
    CartQueue = None

    # instantiate everything
    def __init__(self, master, width):

        self.Master = master

        ###YATES_COMMENT: This may be a dead variable.  No one ever seems to be
        ###                    using self.font, but rather font=('Helvetica', '12', 'bold')
        ###                    as an inline parameter
        ###YATES_ANSWER:  In the calls to Label, passing in self.font flags an
        ###               error, where as saying font=('Helvetica', 12, 'bold')
        ###               does not.
        #self.font = ('Helvetica', 12, 'bold')
        ###YATES_COMMENT: Sets the title and its attributes for the Window.
        self.Title = Label(self.Master, fg='#000', font=('Helvetica', 36, 'bold italic'), text='ZAutomate :: Automation')
        self.Title.grid(row=0, column=0, columnspan=3)


        ###YATES_COMMENT: Initializes the START button on start up.
        ###                    textvariable=self.ButtonContent is how the button text is populated
        ###                    command=self.ButtonHandler defines the call-back function for when the button is pressed
        self.ButtonContent = StringVar()
        self.ButtonContent.set('  START    ')
        self.Button = Button(self.Master, textvariable=self.ButtonContent, command=self.ButtonHandler, width=16, height=2)
        ###YAtES_COMMENT: .config() function bigs the padding, background and foreground color and button style.
        self.Button.config(bd=2, relief='groove', bg='#008500', highlightbackground='#008500')

        self.Button.grid(row=0, column=3)

        ###YATES_COMMENT: Initializes the CartQueue object with a reference master (What is master?)
        ###                    self.UIUpdate sets the callback function
        ###                    for whenever the CartQueue is filled, refilled, updated,
        ###                    started, etc.
        self.CartQueue = CartQueue(self.Master, width, self.UIUpdate)

        ###YATES_COMMENT: Pretty sure the next 20 or so lines come from Tkinter

        ###YATES_COMMENT: Allocates a new frame, and populates the frame with labels for Cue Time, Track Title, Artist Name
        PlistFr = Frame(self.Master, bd=2, relief=SUNKEN)
        Label(PlistFr, font=('Helvetica', 12, 'bold'), anchor=CENTER, width=16, text='Cue Time').grid(row=0, column=0)
        Label(PlistFr, font=('Helvetica', 12, 'bold'), anchor=CENTER, width=32, text='Track Title').grid(row=0, column=1)
        Label(PlistFr, font=('Helvetica', 12, 'bold'), anchor=CENTER, width=32, text='Artist Name').grid(row=0, column=2)

        InPlFr = Frame(PlistFr)
        scroll = Scrollbar(InPlFr, orient="vertical", command=self.ScrollHandler)
        self.CueBox = Listbox(InPlFr, selectmode='single', yscrollcommand=scroll.set, exportselection=0, width=16, height=20)
        self.TrackBox = Listbox(InPlFr, selectmode='single', yscrollcommand=scroll.set, exportselection=0, width=32, height=20)
        self.ArtistBox = Listbox(InPlFr, selectmode='single', yscrollcommand=scroll.set, exportselection=0, width=32, height=20)

        scroll.pack(side="right", fill="y")
        self.CueBox.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        self.TrackBox.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        self.ArtistBox.pack(side="left", fill="x", expand=True, padx=2, pady=2)

        InPlFr.grid(row=1, column=0, columnspan=3)
        PlistFr.grid(row=4, column=0, columnspan=4)

        ###YATES_COMMENT: Initialize the CartQueue with stuff to play.
        self.CartQueue.InitialFill()

    ###YATES_COMMENT: Event Handler for scrolling through the three Windows.
    def ScrollHandler(self, *args):
        self.CueBox.yview(*args)
        self.TrackBox.yview(*args)
        self.ArtistBox.yview(*args)

    ###YATES_COMMENT: ButtonHandler for Start->Stopping->Stopped state machine
    def ButtonHandler(self):
        content = self.ButtonContent.get()
        if content == '  START    ':
            self.AutoStart()
            self.ButtonContent.set('    STOP    ')
            self.Button.config(bg='#FF0', highlightbackground='#FF0')
        elif content == '    STOP    ':
            self.AutoStop()
            self.ButtonContent.set(' STOPPING ')
            self.Button.config(bg='#F00', highlightbackground='#F00')
        elif content == ' STOPPING ':
            self.AutoStopNow()
            self.ButtonContent.set('  START    ')
            self.Button.config(bg='#008500', highlightbackground='#008500')

    ###YATES_COMMENT: Function to Start playing Automation...
    def AutoStart(self, Quiet=True):
        print "Automation :: AutoStart :: Entered Function"
        self.CartQueue.Start(True)
        if Quiet is False:
            print 'Automation starting...'

    ###YATES_COMMENT: Button to Stop playing Automation after this song.
    def AutoStop(self, Quiet=True):
        print "Automation :: AutoStop :: Entered Function"
        self.CartQueue.StopSoon()
        if Quiet is False:
            print 'Automation will stop after this track.'

    ###YATES_COMMENT: Button to stop playing Automation now.
    def AutoStopNow(self, Quiet=True):
        print "Automation :: AutoStopNow :: Entered Function"
        ###YATES_COMMENT: Transition function handles transitioning between
        ###                    starting, stopping and stopped.
        ###                    If called and our queueu is below the minimum threshold
        ###                    it refills the thread;
        ###                    If KeepGoing is true (A cart just finished), dequeues the
        ###                    Cart and plays the next cart.
        ###                    If stopped, we clear out the queue, updated UI and
        ###                    wait to get a new one
        print "Automationp :: AutoStopNow :: Calling CartQueue.Transition"
        self.CartQueue.Transition()

    # callback: when anything happens in CartQueue, run this to update the UI's state
    ###YATES_COMMENT: This is the callback fucntion from the CartQueue that updates
    ###                    The UI.
    def UIUpdate(self):

        ## clear, then reset, the playlist
        ###YATES_COMMENT: What/Where is END?
        ###YATES_ANSWER:  END is a constant/macro from Tkinter whch means the end
        ###                    of some kind of structure.
        ###                    So, these next three lines empty out the Cue/Track/ArtistBox
        self.CueBox.delete(0, END)
        self.TrackBox.delete(0, END)
        self.ArtistBox.delete(0, END)
        ###YATES_COMMENT: Appends the CueTime, TrackName, ArtistName to each of the Boxes.
        for item in self.CartQueue.GetArray():
            self.CueBox.insert(END, item[0])
            self.TrackBox.insert(END, item[1])
            self.ArtistBox.insert(END, item[2])

        ## reset (?) the button
        ###YATES_COMMENT: Presumably, if IsStopping is true, we've pressed the Stop button
        ###                    to stop at the end of the track and nothign will happen between
        ###                    pressing stop and the track ending.  So next time IsStopping is true,
        ###                    set the ButtonContent to start, so next time the button is pushed
        ###                    the ButtonHandler will properly start the music.
        if self.CartQueue.IsStopping():
            self.ButtonContent.set('  START    ')
            self.Button.config(bg='#008500', highlightbackground='#008500')
        ###What is the state of IsStopping after this?  Shouldn't IsStopping be
        ###false, as the UIUpdate is called when we stop?

    # called at close program; cleans everything up
    def Bail(self):
        self.CartQueue.Dequeue()
        self.CartQueue.Save()
        self.Master.destroy()

root = Tk()
root.geometry(WINDOW_PARAMS)

automation = Automation(root, SIZE_X)
root.protocol("WM_DELETE_WINDOW", automation.Bail)
root.title("ZAutomate :: Automation")
root.mainloop()
