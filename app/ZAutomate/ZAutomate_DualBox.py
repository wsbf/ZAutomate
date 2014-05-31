### dual scroll: http://stackoverflow.com/questions/4066974/scrolling-multiple-tkinter-listboxes-together
### pure tcl: http://www.tcl.tk/man/tcl8.4/TkCmd/listbox.htm#M24
### fix dual highlight: http://www.internetcomputerforum.com/python-forum/311559-tkinter-selecting-one-item-each-two-listboxes.html

from Tkinter import *

class DualBox(Frame):
	Size = 0
	SelCallback = None
 	SelNdx = None
	
	def __init__(self, parent):
		Frame.__init__(self, bg='#33CCCC')
		self.SelCallback = parent.SetClipboard
		
		# make scroll bar
		self.vsb = Scrollbar(self, orient="vertical", command=self.onvsb)
		
		label1 = Label(self, text='Track', bg='#33CCCC', fg='#000')
		label2 = Label(self, text='Artist', bg='#33CCCC', fg='#000')
		
		# make two scroll boxes
		self.lb1 = Listbox(self, yscrollcommand=self.vsb.set, exportselection=0, width=40, bg='#000', fg='#33CCCC')
		self.lb2 = Listbox(self, yscrollcommand=self.vsb.set, exportselection=0, width=40, bg='#000', fg='#33CCCC')
		
		# fill the whole screen - pack!
		self.vsb.pack(side="right",fill="y")
		
		label1.pack(side='left', fill='x',expand=True)	
		self.lb1.pack(side="left",fill="x", expand=True, padx=5, pady=5)
		self.lb2.pack(side="left",fill="x", expand=True, padx=5, pady=5)
		label2.pack(side='left',fill='x',expand=True)
		
		# mouse wheel binding
		self.lb1.bind("<MouseWheel>", self.onmousewheel)
		self.lb2.bind("<MouseWheel>", self.onmousewheel)
		
		# onclick binding?
		self.lb1.bind("<<ListboxSelect>>", self.select)
		self.lb2.bind("<<ListboxSelect>>", self.select)
		
	def TupleFill(self, tuplearr):
		self.Clear()
		for tuple in tuplearr:
			self.lb1.insert(END, tuple[0])
			self.lb2.insert(END, tuple[1])
		self.Size = len(tuplearr)
	
	def ProtoFill(self, length):
		self.Clear()
		# prototype - fill array
		for i in range(length):
			self.lb1.insert("end","item %s" % i)
			self.lb2.insert("end","item %s" % i)
		self.Size = length
	
	def Clear(self):
		self.lb1.delete(0, END)
		self.lb2.delete(0, END)
		self.Size = 0
	
	
	def select(self, *args):
		ndx = self.GetSelNdx()
		
		##print "DualBox :: clicked selection " + (str)(ndx)
		
		if ndx is not None:
			self.lb1.selection_clear(0, self.Size)
			self.lb2.selection_clear(0, self.Size)
			self.lb1.selection_set(ndx,ndx)
			self.lb2.selection_set(ndx,ndx)
		
		self.SelCallback(ndx)
	
	def GetSelNdx(self):
		one = self.lb1.curselection()
		two = self.lb2.curselection()
		if len(one) is 0:
			one = None
		else:
			one = one[0]
		if len(two) is 0:
			two = None
		else:
			two = two[0]
		
		if one is None and two is None:
			pass
		elif one is not None and two is None:
			self.SelNdx = one
		elif one is None and two is not None:
			self.SelNdx = two
		elif one is not None and two is not None:
			if one == self.SelNdx:
				self.SelNdx = two
			elif two == self.SelNdx:
				self.SelNdx = one
			
		return self.SelNdx
	
	
	# scroll handler
	def onvsb(self, *args):
		self.lb1.yview(*args)
		self.lb2.yview(*args)
	
	
	# wheel handler
	def onmousewheel(self, event):
		self.lb1.yview("scroll", event.delta,"units")
		self.lb2.yview("scroll",event.delta,"units")
		# this prevents default bindings from firing, which
		# would end up scrolling the widget twice
		return "break"
	