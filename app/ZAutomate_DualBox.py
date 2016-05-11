### dual scroll: http://stackoverflow.com/questions/4066974/scrolling-multiple-tkinter-listboxes-together
### pure tcl: http://www.tcl.tk/man/tcl8.4/TkCmd/listbox.htm#M24
### fix dual highlight: http://www.internetcomputerforum.com/python-forum/311559-tkinter-selecting-one-item-each-two-listboxes.html

"""The DualBox module provides the DualBox class."""
import Tkinter
from Tkinter import Frame, Scrollbar, Label, Listbox

class DualBox(Frame):
    """The DualBox class is a pair of Listboxes that has a list of carts."""
    _prev_index = None
    _select_callback = None

    _list_box1 = None
    _list_box2 = None

    def __init__(self, parent):
        """Construct a DualBox.

        :param parent
        """
        Frame.__init__(self, bg='#33CCCC')
        self._select_callback = parent.select_cart

        # make scroll bar
        scroll_bar = Scrollbar(self, orient="vertical", command=self.onvsb)

        label1 = Label(self, text='Track', bg='#33CCCC', fg='#000')
        label2 = Label(self, text='Artist', bg='#33CCCC', fg='#000')

        # make two scroll boxes
        self._list_box1 = Listbox(self, yscrollcommand=scroll_bar.set, exportselection=0, width=40, bg='#000', fg='#33CCCC')
        self._list_box2 = Listbox(self, yscrollcommand=scroll_bar.set, exportselection=0, width=40, bg='#000', fg='#33CCCC')

        # fill the whole screen - pack!
        scroll_bar.pack(side="right", fill="y")

        label1.pack(side='left', fill='x', expand=True)
        self._list_box1.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self._list_box2.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        label2.pack(side='left', fill='x', expand=True)

        # mouse wheel binding
        self._list_box1.bind("<MouseWheel>", self.onmousewheel)
        self._list_box2.bind("<MouseWheel>", self.onmousewheel)

        # onclick binding?
        self._list_box1.bind("<<ListboxSelect>>", self.select)
        self._list_box2.bind("<<ListboxSelect>>", self.select)

    def fill(self, carts):
        """Fill the DualBox with a list of carts.

        :param carts: array of carts
        """
        self._list_box1.delete(0, Tkinter.END)
        self._list_box2.delete(0, Tkinter.END)

        for cart in carts:
            self._list_box1.insert(Tkinter.END, cart.title)
            self._list_box2.insert(Tkinter.END, cart.issuer)

    def _get_selected_index(self):
        one = self._list_box1.curselection()
        two = self._list_box2.curselection()

        if len(one) is 0:
            one = None
        else:
            one = one[0]

        if len(two) is 0:
            two = None
        else:
            two = two[0]

        if one is not None and two is not None:
            if one == self._prev_index:
                self._prev_index = two
            elif two == self._prev_index:
                self._prev_index = one
        elif one is not None:
            self._prev_index = one
        elif two is not None:
            self._prev_index = two

        return self._prev_index

    def select(self, *args):
        """Select an item in the DualBox.

        :param args
        """
        index = self._get_selected_index()

        if index is not None:
            self._list_box1.selection_clear(0, Tkinter.END)
            self._list_box2.selection_clear(0, Tkinter.END)
            self._list_box1.selection_set(index, index)
            self._list_box2.selection_set(index, index)

        self._select_callback(index)

    # scroll handler
    def onvsb(self, *args):
        self._list_box1.yview(*args)
        self._list_box2.yview(*args)

    # wheel handler
    def onmousewheel(self, event):
        self._list_box1.yview("scroll", event.delta, "units")
        self._list_box2.yview("scroll", event.delta, "units")
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"
