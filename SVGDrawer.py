# -*- coding: utf-8 -*-
from Tkinter import *
from tkFileDialog import askopenfile,askopenfilename
from SVG import SVGRenderer
from GMaker import GMaker
from geometry import Metrics
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

class SVGDrawerUI:
	renderer = None
	gmaker = None
	infile = None
	infilename = None
	config = RawConfigParser()
	vars = {}
	
	# file > cfg ; ui > cfg ; cfg > var ; var > cfg
	def readConfig(self):
		
		# set from defaults
		for section in defaults:
			self.config.add_section(section)
			for name in defaults[section]:
				self.config.set(section,name,defaults[section][name])
		
		f = getConfigFile()
		if os.path.exists(f):
			self.config.readfp(open(f,'r'))
		else:
			sf = open(f,'w')
			self.config.write(sf)
			
		for section in self.config.sections():
			self.vars[section] = {}
			for name in self.config.options(section):
				self.vars[section][name] = StringVar(self.win,str(self.config.get(section,name)))
				
	
	def saveConfig(self):
		self.config.write(open(getConfigFile(),'w'))
	
	def updateConfig(self):
		for section in self.vars:
			for name in self.vars[section]:
				cval = self.vars[section][name].get()
				if self.config.get(section,name) != cval:
					self.config.set(section,name,cval)
		self.saveConfig()
	
	def makeMainMenu(self,master):
		self.menubar = Menu(master, tearoff=0)
		
		filemenu = Menu(self.menubar, tearoff=0)
		filemenu.add_command(label="Open", command=self._select_file)
		self.menubar.add_cascade(label="File", menu=filemenu)
		
		master.config(menu=self.menubar)
	
	def __init__(self,master):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.quit)
		# read defaults an init config
		
		self.makeMainMenu(master);
		
		# main window
		self.win = Frame(master,width=800)
		self.win.pack()
		
		opts = Frame(self.win)
		opts.pack(side=LEFT)
		
		self.readConfig()
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
		scale = float(self.canvas.winfo_width())/200.0
		for line in self.gmaker.draws:
			self.canvas.create_line(line.p0.x*scale,line.p0.y*scale,line.pn.x*scale,line.pn.y*scale,fill='#666666')
		return
		for line in self.gmaker.draws:
			self.canvas.create_line(line.p0.x*scale,line.p0.y*scale,line.pn.x*scale,line.pn.y*scale,fill='#ff0000')
		
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

