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
		self.moves=[]
		self.draws=[]
		
	def getDrawingCode(self):
		t1 = Point(-1,1)
		G="G1 F%d\n"%self.feedrate
		xmin = float('inf')
		xmax = -float('inf')
		for form in self.data.forms:
			xmin = min(form.bounds.p0.x,xmin)
			xmax = max(form.bounds.pn.x,xmax)
		t2 = Point(xmin + xmax,0)
		for form in self.data.forms:
			do_border = form.border_width >= float(self.border_settings["width_threshold"])
			do_border = do_border and form.border_color >= float(self.border_settings["color_threshold"])
			
			do_fill =  True
			lastP = None
			print do_border
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
				fillsteps = int(self.fill_settings['hatching_layers']) * int(self.fill_settings['hatching_density_steps'])
				start = (math.pi*2)*(float(self.fill_settings['angle'])/360.0)
				
				
				step = math.pi/float(self.fill_settings['hatching_layers'])
				angles = []
				for i in range(int(self.fill_settings['hatching_layers'])):
					angles.append(start + step*i)
				angles = [math.pi*0.625,math.pi*0.75]
				angles = [math.pi*0.125,math.pi*0.25,math.pi*0.375,math.pi*0.5,math.pi*0.625,math.pi*0.75]
				angles = [math.pi*0.125]
				#angles = []
				stepfill = float(form.fill) / 255.0
				brk = float(fillsteps) * stepfill
				i=0
				for angle in angles:
					if i>=brk: break;
					i+=1
					odd = False
					density = 2
					for line in form.getHatchingLayer(angle,density):
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
			
		G+="G1 Z%d\n"%self.endZ
		return G
	
