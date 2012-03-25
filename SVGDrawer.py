# -*- coding: utf-8 -*-
from Tkinter import *
from tkSimpleDialog import Dialog
from tkFileDialog import askopenfile,askopenfilename
from SVG import SVGRenderer
from GMaker import GMaker
from geometry import Metrics,Point
from ConfigParser import RawConfigParser
import sys,os


import gettext
_ = gettext.gettext


"""
Machine
(float) Drawing Z
(flaot) Traveling Z


how to deal with borders:
- ignore borders below 0___255 

[x] Fill Method Hatching
- fill layers 1___10
- starting at angle 0___180
- minimal density ___ lines/cm
- maximum density ___ lines/cm

[ ] Fill Method Z
- Move Z between Drawing Z - (float) and (float)

- density 0___50 lines/cm
- moving angle 0___180
"""

defaults={
	'private':{
		'last_directory':os.environ['HOME'],
		'profiles':'{}'
	},
	'parse':{
		'precision':1.0 # or 10.0, 0.1, 0.01,
	},
	'machine':{
		'drawing_z':1.0, # white
		'traveling_z':3.0,
		'feedrate':480
	},
	'border':{
		'type':'threshold', # or z
		'width_threshold':0.5,
		'color_threshold':32,
		# 
		'z':0,
		'z_affected_by':'width' # color, both
	},
	'fill':{
		'type':'hatching', # or z or threshold
		'angle':30,
		'angle_stepwidth':30,
		'hatching_layers':3,
		'hatching_min_density':2.0,
		'hatching_max_density':10.0,
		'hatching_density_steps':5,

		'z_density':5.0, # lines/cm
		
	},
}




def getConfigFile():
	#mac
	if sys.platform == 'darwin':
		return os.path.expanduser('~/Library/Preferences/SVGDrawer.ini')
	# 
	#
	#if sys.platform == 'win32': # i hate windows and i currently ignore it
	#	return os.path.expanduser()


class Askname(Toplevel):
	
	
	def __init__(self,parent,variable=None,label="Name",title="Choose a name..."):
		Toplevel.__init__(self,parent)
		self.transient(parent)
		self.title(title)
		self.parent=parent
		self.result=None
		body = Frame(self)
		self.initial_focus = self.body(body)
		body.pack(padx=5, pady=5)
		
		self.var = variable
		Label(self, text=label).pack(side=LEFT,padx=10)
		Entry(self, textvariable=variable).pack(side=LEFT,padx=10)
	
		Button(self, text="Cancel", command=self.cancel).pack(side=LEFT,pady=5)
		Button(self, text="Okay", command=self.okay).pack(side=LEFT,pady=5)
		
		
		self.grab_set()
		if not self.initial_focus:
			self.initial_focus = self
		self.protocol("WM_DELETE_WINDOW", self.cancel)
		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
									parent.winfo_rooty()+50))
		
		self.initial_focus.focus_set()
		self.wait_window(self)
		pass
		
	def body(self,master):
		pass
		
	def cancel(self,event=None):
		self.parent.focus_set()
		self.destroy()
	
	def okay(self, event=None):
		self.result = self.var
		self.withdraw()
		self.update_idletasks()
		self.cancel()
		
	
def askforname(parent):
	var = StringVar(parent,_("No name..."))
	a = Askname(parent,var)
	if a.result: 
		return a.result.get()
	return None
	

class SVGDrawerUI:
	renderer = None
	gmaker = None
	infile = None
	infilename = None
	config = RawConfigParser()
	vars = {}
	profiles = []
	
	# file > cfg ; ui > cfg ; cfg > var ; var > cfg
	def readConfig(self):
		
		# set from defaults
		for section in defaults:
			self.config.add_section(section)
			for name in defaults[section]:
				self.config.set(section,name,defaults[section][name])
		
		# write defaults if not exist
		f = getConfigFile()
		if os.path.exists(f):
			self.config.readfp(open(f,'r'))
		else:
			sf = open(f,'w')
			self.config.write(sf)
		
		
		for section in self.config.sections():
			self.vars[section] = {}
			for name in self.config.options(section):
				if section+name in ['privateprofiles']:
					continue
				self.vars[section][name] = StringVar(self.win,str(self.config.get(section,name)))
		
		
		self.profiles = eval(self.config.get('private','profiles'))
		#for a in self.profiles: self.profiles[a] = eval(self.profiles[a])
	
	def saveConfig(self):
		self.config.write(open(getConfigFile(),'w'))

	def saveCurrentProfile(self):
		name = askforname(self.master)
		if not name: 
			return
		self.profiles[name] = repr(self.getCurrentProfile())
		self.updateConfig()
		
		
	def selectProfile(self,name="nix"):
		for section in self.profiles[name]:
			for var in self.profiles[name][section]:
				self.vars[section][var].set(self.profiles[name][section][var]);
		
		pass
		
	def getCurrentProfile(self):
		c = {}
		for section in self.vars:
			if section in ['private']:
				continue
			c[section] = {}
			for name in self.vars[section]:
				c[section][name] = self.vars[section][name].get()
		return c
		
	def updateConfig(self):
		for section in self.vars:
			for name in self.vars[section]:
				cval = self.vars[section][name].get()
				if self.config.get(section,name) != cval:
					self.config.set(section,name,cval)
		self.config.set('private','profiles',repr(self.profiles))
		self.saveConfig()
	
	
	def makeMainMenu(self,master):
		self.menubar = Menu(master, tearoff=0)
		
		filemenu = Menu(self.menubar, tearoff=0)
		filemenu.add_command(label="Open", command=self._select_file)
		self.menubar.add_cascade(label="File", menu=filemenu)

		filemenu = Menu(self.menubar, tearoff=0)
		filemenu.add_command(label="Save current profile...", command=self.saveCurrentProfile)
		filemenu.add_separator()
		
		for name in self.profiles:
			filemenu.add_command(label=name, command=lambda name=name: self.selectProfile(name))
		
		self.menubar.add_cascade(label="Profiles", menu=filemenu)
		
		master.config(menu=self.menubar)
	
	def __init__(self,master):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.quit)
		# read defaults an init config
		
		
		# main window
		self.win = Frame(master,width=800)
		self.win.pack()
		
		opts = Frame(self.win)
		opts.pack(side=LEFT)
		
		self.readConfig()
		self.makeMainMenu(master);
		
		br = Frame(opts)
		br.pack(padx=10,fill='x')
		
		# parse settings
		# precision in 1/100, 1/10, 1 mm
		# scale, move, start at x/y=0
		# 
		
		
		# select file
		Button(br,text=_("Select File ..."),command=self._select_file).pack(side=LEFT)
		self.runbut = Button(br,text=_("Run"), command=self.do_convert,state = DISABLED)
		self.runbut.pack(side=RIGHT)
		
		self.filename_label = Label(br,text='')
		self.filename_label.pack(side=LEFT)
		
		fr = LabelFrame(opts,bd=1,text=_("Parsing:"))
		fr.pack(padx=10,pady=10,ipadx=10,ipady=10,expand="yes",fill='both')

		section='parse'
		name='precision'
		options = 10.0, 1.0, 0.1, 0.01
		Label(fr, text=_("Precision:")).pack(side=LEFT)
		apply(OptionMenu,(fr,self.vars[section][name])+options).pack(side=LEFT)
		Label(fr, text=_("mm")).pack(side=LEFT)
		
		
		# machine settings
		fr = LabelFrame(opts,bd=1,text=_("Machine settings:"))
		fr.pack(padx=10,pady=10,ipadx=10,ipady=10,expand="yes",fill='both')

		section='machine'
		
		name='traveling_z'
		Label(fr, text=_("Traveling Z:")).grid(row=0,column=0)
		Entry(fr, text="0", exportselection=0,textvariable=str(self.vars[section][name])).grid(row=0,column=1)
		Label(fr, text=_("mm")).grid(row=0,column=3)
		
		name='drawing_z'
		Label(fr, text=_("Drawing Z:")).grid(row=1,column=0)
		Entry(fr, text="0", exportselection=0,textvariable=str(self.vars[section][name])).grid(row=1,column=1)
		Label(fr, text=_("mm")).grid(row=1,column=3)
		
		
		name='feedrate'
		Label(fr, text=_("Feedrate:")).grid(row=2,column=0)
		Entry(fr, exportselection=0,textvariable=str(self.vars[section][name])).grid(row=2,column=1)
		Label(fr, text=_("steps/sec.")).grid(row=2,column=3)
		
		# define bounding box: x,y,w,h
		
		
		# border settings
		section='border'
		fr = LabelFrame(opts,bd=1,text=_("Border options:"))
		fr.pack(padx=10,pady=10,ipadx=10,ipady=10,expand="yes",fill='both')

		name='type'
		f = Frame(fr)
		f.pack(expand='yes',fill='both')
		Radiobutton(f, text=_('Threshold'), variable=str(self.vars[section][name]), value='threshold',command=self._select_border).pack(side=LEFT,anchor=W)
		Radiobutton(f, text=_('Z'), variable=str(self.vars[section][name]), value='z',command=self._select_border).pack(side=LEFT,anchor=W)
		
		f = Frame(fr)
		f.pack(expand='yes',fill='both')
		
		name='width_threshold'
		Label(f, text=_("Border width threshold: ")).grid(row=0,column=0)
		Entry(f, exportselection=0,textvariable=str(self.vars[section][name])).grid(row=0,column=1)
		
		name='color_threshold'
		Label(f, text=_("Border color threshold: ")).grid(row=1,column=0)
		Entry(f, textvariable=str(self.vars[section][name]), exportselection=0).grid(row=1,column=1)
		
		
		section='fill'
		
		# fillsettings
		fr = LabelFrame(opts,bd=1,text=_("Fill options:"))
		fr.pack(padx=10,pady=10,ipadx=10,ipady=10,expand="yes",fill='both')
		
		name='type'
		f = Frame(fr)
		f.pack(expand='yes',fill='both')
		Radiobutton(f, text=_('Hatching'), variable=str(self.vars[section][name]), value='hatching',command=self._select_border).pack(side=LEFT,anchor=W)
		Radiobutton(f, text=_('Z'), variable=str(self.vars[section][name]), value='z',command=self._select_border).pack(side=LEFT,anchor=W)
		
		f = Frame(fr)
		f.pack(expand='yes',fill='both')
		name,row='angle',0
		Label(f, text=_("Angle: ")).grid(row=row,column=0)
		Entry(f, exportselection=0,textvariable=str(self.vars[section][name])).grid(row=row,column=1)
		Label(f, text=_("°")).grid(row=row,column=2)
		
		name,row='hatching_layers',1
		Label(f, text=_("Hatching Layers: ")).grid(row=row,column=0)
		Entry(f, exportselection=0,textvariable=str(self.vars[section][name])).grid(row=row,column=1)
		
		name,row='angle_stepwidth',2
		Label(f, text=_("Stepwidth: ")).grid(row=row,column=0)
		Entry(f, exportselection=0,textvariable=str(self.vars[section][name])).grid(row=row,column=1)
		Label(f, text=_("°")).grid(row=row,column=2)
		
		f = Frame(fr)
		f.pack(expand='yes',fill='both')
		name='hatching_min_density'
		Label(f, text=_("Density min: ")).pack(side=LEFT)
		Entry(f, width=6, exportselection=0,textvariable=str(self.vars[section][name])).pack(side=LEFT)
		Label(f, text=_("max:")).pack(side=LEFT)
		name = 'hatching_max_density'
		Entry(f, width=6, exportselection=0,textvariable=str(self.vars[section][name])).pack(side=LEFT)
		Label(f, text=_("lines/cm")).pack(side=LEFT)
		name = 'hatching_density_steps'
		Label(f, text=_("Steps")).pack(side=LEFT)
		Entry(f, width=6, exportselection=0,textvariable=str(self.vars[section][name])).pack(side=LEFT)
		
		f = Frame(fr)
		f.pack(expand='yes',fill='both')
		
		
		#'z_density':5.0, # lines/cm

		# self.fill_method hatch / z radio-button
		# self.fill_angle 
		
		# self.fill_hatch_min_density Label+Entry
		# self.fill_hatch_max_density Label+Entry
		# self.fill_hatch_count_layers
		
		# self.fill_z_density
		self.win.update()
		self.canvas = Canvas(self.win,width=self.win.winfo_height(),height=self.win.winfo_height(),bg='#cccccc')
		self.canvas.pack(side=RIGHT)
		
		# open file > starts convert!
		# progress indicator
		# result view
	
	def quit(self):
		self.updateConfig()
		base.destroy()
		pass
	
	
	def _select_border(self):
		self.config.set('border','type',self.vars['border']['type'].get())
	
	def _select_file(self):
		selected_file = askopenfilename(filetypes=[(_("SVG Files"),'*.svg')],initialdir=self.config.get('private','last_directory'))
		if selected_file=='': # user abort
			return
		self.runbut["state"] = ACTIVE
		self.infilename = selected_file
		# set filename onto
		self.filename_label["text"] = os.path.basename(self.infilename)
		# save last directory to settings
		self.config.set('private','last_directory',os.path.dirname(self.infilename))
		self.saveConfig()
	
	def draw(self):
		# make
		self.canvas.delete(ALL)
		scale = float(self.canvas.winfo_width()-20) / max(self.gmaker.pmax.x,self.gmaker.pmax.y)
		w = (self.gmaker.pmax.x-self.gmaker.pmin.x)*scale
		h = (self.gmaker.pmax.y-self.gmaker.pmin.y)*scale
		move = Point((float(self.canvas.winfo_width())-w)/2.0,(float(self.canvas.winfo_height())-h)/2.0) + Point(10,10)

		for line in self.gmaker.draws:
			self.canvas.create_line( move.x+line.p0.x*scale, move.y+line.p0.y*scale, move.x+line.pn.x*scale, move.y+line.pn.y*scale, fill='#666666')
		
		
		# rulers
		self.canvas.create_rectangle(0,0,self.canvas.winfo_width(),10,fill='#999999',width=0)
		self.canvas.create_rectangle(0,10,10,self.canvas.winfo_height(),fill='#999999',width=0)
		#self.canvas.create_line(0,10,self.canvas.winfo_width(),10,fill='#000000',border=None)
		#self.canvas.create_line(10,0,10,self.canvas.winfo_height(),fill='#000000',border=None)
		
		fct=5
		i=0
		x = move.x
		while x < self.canvas.winfo_width():
			if (i%10) == 0: 
				l=10
				self.canvas.create_text(x+1,2,anchor=NW,text=str(fct*i),font=("Helvetica",9,"normal"))
			else: 
				l=5
			self.canvas.create_line(x,10-l,x,10,fill='#000000')
			x+=fct*scale
			i+=1
		
		i=0
		y = move.y
		while y < self.canvas.winfo_height():
			if (i%10) == 0: 
				l=10
				self.canvas.create_text(2,y+1,anchor=NW,text=str(fct*i),font=("Helvetica",9,"normal"))
			else: 
				l=5
			self.canvas.create_line(10-l,y,10,y,fill='#000000')
			y+=fct*scale
			i+=1
			
		#self.canvas.create_line(move.x-5, move.y, move.x+5, move.y, fill='#ff0000')
		#self.canvas.create_line(move.x, move.y-5, move.x, move.y+5, fill='#ff0000')
		
		
	def can_convert(self):
		return self.infilename != None and os.path.exists(self.infilename)
		
	def do_convert(self):
		if not self.can_convert(): 
			# put some error message
			return False
		self.updateConfig()
		self.infile = open(self.infilename,'r')
		self.interpreter = SVGRenderer(precision=float(self.config.get("parse","precision")))
		self.interpreter.parseFile(self.infile)
		self.gmaker = GMaker(self.interpreter,machine=self.config.items('machine'),border=self.config.items('border'),fill=self.config.items('fill'))
		
		self.outfile=open(self.infilename+".gcode",'w')
		self.outfile.write(self.gmaker.getDrawingCode())
		self.outfile.close()
		
		self.draw()
		

	
base = Tk()
app = SVGDrawerUI(base)

base.mainloop()

