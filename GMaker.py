from SVG import LinearMoves
import math
from geometry import Point,Line




class GMaker:
	
	liftZ = 2.0
	endZ = 30
	offsetZ = 11
	feedrate = 480
	density = 0.5
	
	do_border = True
	do_fill = False
	'''
	Machine
	(float) Drawing Z
	(flaot) Traveling Z
	
	
	how to deal with borders:
	- ignore borders below 0___255 
	
	[x] Fill Method Hatching
	- fill layers 0___10
	- starting at angle 0___180
		- minimal density ___ lines/cm
		- maximum density ___
		- steps
	
	[ ] Fill Method Z
	- Move Z between Drawing Z - (float) and (float)
	
	- density 0___50 lines/cm
	- moving angle 0___180
	
	'''
	
	'''
	'machine':{
		'drawing_z':1.0,
		'traveling_z':3.0,
		'feedrate':480
	},
	'border':{
		'type':'threshold', # or z
		'width_threshold':0.5,
		'color_threshold':32,
		
		'z':0,
		'z_affected_by':'width' # color, both
	},
	'fill':{
		'type':'hatching', # or z or threshold
		'angle':30,
		'hatching_layers':3,
		'hatching_min_density':2.0,
		'hatching_max_density':10.0,
		'hatching_density_steps':5,

		'z_density':5.0, # lines/cm
		
	},
	'''
	
	machine_settings = {}
	border_settings = {}
	fill_settings = {}
	
	def __init__(self,data,machine=[],border=[],fill=[]):
		#if not isinstance(data, LinearMoves):
		#	raise TypeError("'data' is not of type LinearMoves")
		for k,v in machine: self.machine_settings[k] = v
		for k,v in border: self.border_settings[k] = v
		for k,v in fill: self.fill_settings[k] = v
		
		self.data = data
		
		# make angles
		start = ((math.pi*2)*(float(self.fill_settings['angle'])/360.0))
		anglestep = math.pi/float(self.fill_settings['hatching_layers'])
		self.angles = [start + anglestep*i for i in range(int(self.fill_settings['hatching_layers']))]
		
		self.moves=[]
		self.draws=[]
		
	def getDrawingCode(self):
		
		G="G92 X0 Y0 Z0 E0\n"
		G+="G1 F%d\n"%self.feedrate # set feedrate
		self.pmin = Point(float('inf'),float('inf'))
		self.pmax = Point(float('-inf'),float('-inf'))
		for form in self.data.forms:
			self.pmin.x = min(form.bounds.p0.x,self.pmin.x)
			self.pmin.y = min(form.bounds.p0.y,self.pmin.y)
			self.pmax.x = max(form.bounds.pn.x,self.pmax.x)
			self.pmax.y = max(form.bounds.pn.y,self.pmax.y)
		
		
		# start drawing at 0/0
		for i in range(len(self.data.forms)):
			self.data.forms[i] = self.data.forms[i] - self.pmin
		self.pmin = Point(0,0)
		self.pmax = self.pmax - self.pmin
		
		# scale and move parameter ...
		t1 = Point(-1,1)
		t2 = Point(self.pmax.x,0)
		
		for form in self.data.forms:
			do_border = form.border_width >= float(self.border_settings["width_threshold"])
			do_border = do_border and form.border_color >= float(self.border_settings["color_threshold"])
			
			do_fill =  True
			lastP = None
			
			if do_border:
				lines = form.getLines()
				
				coord = ((lines[0][1].p0*t1)+t2).value()
				G+="G1 Z%s ; lift Z\n" % self.machine_settings["traveling_z"]
				G+="G1 X%f Y%f\n" % coord
				G+="G1 Z%s ; return Z\n" % self.machine_settings["drawing_z"]
				
				for cmd,l in lines:
					if cmd == 'move':
						G+="G1 Z%s ; lift Z\n" % self.machine_settings["traveling_z"]
						curr = self.moves
					else:
						curr = self.draws
					G+="G1 X%f Y%f\n" % ((l.pn*t1)+t2).value()
					if cmd == 'move':
						G+="G1 Z%s ; return Z\n" % self.machine_settings["drawing_z"]
					
					curr.append(l)
					lastP = ((l.pn*t1)+t2)
					
			if do_fill:
				brk = (float(form.fill) / 255.0) * len(self.angles)
				densities = [10.0/float(self.fill_settings['hatching_max_density']) for i in range(int(brk))]
				last = brk - math.floor(brk)
				if last>0:
					densities.append(10/(float(self.fill_settings['hatching_min_density'])+last*(float(self.fill_settings['hatching_max_density'])-float(self.fill_settings['hatching_min_density']))))
				i=0
				for density in densities:
					odd = False
					for line in form.getHatchingLayer(self.angles[i],density):
						#if odd: f = f.reverse()
						for f in line:
							coord = ((f.p0*t1)+t2).value()
							G+="G1 Z%s ; lift Z\n" % self.machine_settings["traveling_z"]
							G+="G1 X%f Y%f\n" % coord
							G+="G1 Z%s ; return Z\n" % self.machine_settings["drawing_z"]
							G+="G1 X%f Y%f\n" % ((f.pn*t1)+t2).value()
							if lastP != None:
								self.moves.append(Line(lastP,((f.pn*t1)+t2)))
							self.draws.append(f)
							lastP = ((f.pn*t1)+t2)
					i+=1
			
		G+="G1 Z%d\n"%self.endZ
		return G
	
