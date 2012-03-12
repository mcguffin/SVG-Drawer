import re
from types import *
from pprint import pprint
from geometry import Metrics,CubicBezier,Point
import math


'''
M63.046,24.547
	c-3.864,3.864-22.48,8.49-22.48,8.49
	s4.625-18.617,8.489-22.481
	c3.863-3.863,10.127-3.863,13.991,0
	C66.909,14.419,66.909,20.683,63.046,24.547
	z



M54.053,112.329
	c-11.189,0-20.26-9.07-20.26-20.26
	c0-11.189,9.071-20.26,20.26-20.26
	h14.099
	v-0.32
	c0-15.656-12.691-28.347-28.346-28.347
	c-15.656,0-28.347,12.691-28.347,28.347
	v28.346
	c0,15.655,12.691,28.347,28.347,28.347
	c11.171,0,20.828-6.464,25.447-15.854
	H54.053
	z


PATH attributes
	stroke : color | none; default=none
	stroke-miterlimit : float
	stroke-width : float
	fill : url | color | none; default=#000000
	d : (points)



shapes:
RECT
CIRCLE
ELLIPSE
LINE
POLYLINE
POLYGON
PATH

relevant for display
CLIPPATH

relevant for drawing (later...)
G




ToDo:
- mirror
- lifz z after print
- implement feedrate
'''


class GMaker:
	lines=[]
	funcmap={}
	nodeNames = ["rect","circle","ellipse","line","polyline","polygon","path","svg"]
	liftZ = 3
	endZ = 30
	offsetZ = 0
	feedrate = 480
	
	def __init__(self,precision=Metrics.mm):
		# create functions to be called from svg-nodes
		for nn in self.nodeNames:
			self.funcmap[nn]= eval('self.'+nn)
			
		self.precision = precision
		pass
	
	def startElement(self,name,attrs):
		self[name](attrs)
		pass

	def endElement(self,name):
		self[name](None,end=True)
		pass

	def characterData(self,data):
		# don't care
		pass
	
	def getPerforationCode(self):
		# split lines according to self.precision
		# moveto, down, up
		pass

	def getCutterCode(self):
		# split lines according to self.precision
		# moveto, set E, down, up
		pass
	
	def getDrawingCode(self):
		G="G1 F%d\n"%self.feedrate
		for l in self.lines:
			cmd = l["cmd"]
			coord = l["args"]
			if cmd=='M':
				G+="G1 Z%d ; lift Z\n" % self.liftZ
				G+="G1 X%f Y%f\n" % coord
				G+="G1 Z%d ; return Z\n" % self.offsetZ
			elif cmd == 'H':
				G+="G1 X%f\n" % coord
			elif cmd == 'V':
				G+="G1 Y%f\n" % coord
			elif cmd == 'L':
				G+="G1 X%f Y%f\n" % coord
		G="G1 Z%d\n"%self.endZ
		
		
		return G
	
	# nodes
	
	def svg(self,attrs,end=False):
		if (end):
			#pprint( self.lines)
			pass
	
	# transformation
	def g(self,attrs,end=False):
		pass
	
	# shapes
	def circle(self,attrs,end=False):
		if end: return
		r = float(attrs["r"])*unit
		x = float(attrs["cx"])*unit
		y = float(attrs["cy"])*unit
		
		attrs["rx"] = attrs["ry"] = attrs["r"]
		return self.ellipse(attrs)
		
	def ellipse(self,attrs,end=False):
		if end: return
		rx = float(attrs["rx"])*unit
		ry = float(attrs["ry"])*unit
		x = float(attrs["cx"])*unit
		y = float(attrs["cy"])*unit
		
		steps = max(3,int((math.pi*((rx+ry)*0.5)*2)/self.precision))
		angstep = 2*math.pi/steps
		self._mov(x+rx,y)
		for i in range(steps):
			phi=i*angstep
			self._lin(x + math.cos(phi)*rx, y + math.sin(phi)*ry)
		self._lin(x+rx,y) # close form
		
	def rect(self,attrs,end=False):
		if end: return
		x=float(attrs["x"])*unit
		y=float(attrs["y"])*unit
		w=float(attrs["width"])*unit
		h=float(attrs["height"])*unit
		self._mov(x,y)
		self._hor(x+w)
		self._ver(y+h)
		self._hor(x)
		self._ver(y)
		pass

	def line(self,attrs,end=False):
		if end: return
		x1=float(attrs["x1"])*unit
		y1=float(attrs["y1"])*unit
		x2=float(attrs["x2"])*unit
		y2=float(attrs["y2"])*unit
		self._mov(x1,y1)
		self._lin(x2,y2)
		# convert to path
		pass
		
	def polyline(self,attrs,end=False):
		if end: return
		points = attrs["points"].split()
		x,y = eval("("+points[0]+")")
		self._mov(x*unit,y*unit)
		for p in points:
			x,y = eval("("+p+")")
			self._lin(x*unit,y*unit)
		return points
		
	def polygon(self,attrs,end=False):
		if end: return
		points = self.polyline(attrs)
		# close
		x,y = eval("("+points[0]+")")
		self._lin(x*unit,y*unit)
		
	def path(self,attrs,end=False):
		if end: return
		self.curX = self.curY = 0
		commands = self.parse_d(attrs["d"])
		for cm in commands:
			cmd = cm["cmd"]
			args = cm["args"]
			if cmd=='M':
				self.curX,self.curY=args
				self._mov(self.curX,self.curY)
			elif cmd=='m':
				self.curX+=args[0]
				self.curY+=args[1]
				self._mov(self.curX,self.curY)
			elif cmd=='L':
				self.curX,self.curY=args
				self._lin(self.curX,self.curY)
			elif cmd=='l':
				self.curX+=args[0]
				self.curY+=args[1]
				self._lin(self.curX,self.curY)
			elif cmd=='H':
				self.curX=args[0]
				self._hor(self.curX)
			elif cmd=='h':
				self.curX+=args[0]
				self._hor(self.curX)
			elif cmd=='V':
				self.curY=args[0]
				self._ver(self.curY)
			elif cmd=='v':
				self.curY+=args[0]
				self._ver(self.curY)
			
			elif cmd=="C":
				self.bezier(args)
				
			elif cmd=="c":
				for i in range(len(args)):
					if 0 == (i%2):
						args[i]+=self.curX
					else:
						args[i]+=self.curY

				self.bezier(args)
				
			elif cmd=="S":
				# prepend mirror of last 
				p=Point(self.lastcX,self.lastcY)-Point(self.curX,self.curY)
				p2 = Point(self.curX,self.curY)-p
				self.bezier([p2.x,p2.y]+args)
				
				#self.lastcX,self.lastcY,curX,curY=args
				pass
			elif cmd=="s":
				# prepend mirror of last c and 
				p=Point(self.lastcX,self.lastcY)-Point(self.curX,self.curY)
				p2 = Point(self.curX,self.curY)-p
				for i in range(len(args)):
					if 0 == (i%2):
						args[i]+=self.curX
					else:
						args[i]+=self.curY
				self.bezier([p2.x,p2.y]+args)
				#curX+=args[2]
				#curY+=args[3]
				pass
			
			# qadratic bezier --- different math...
			elif cmd=="Q":
				pass
			elif cmd=="q":
				pass
				
			elif cmd=="T":
				pass
			elif cmd=="t":
				pass
				
			elif cmd=="A":
				pass
			elif cmd=="a":
				pass
				
			elif cmd=="Z":
				pass
			elif cmd=="z":
				pass
				
			# c,C,s,S,z,Z,q,Q,t,T,a,A
			
		pprint(commands)
		pass
	
	def bezier(self,args):
		bz=CubicBezier.fromCoords(*([self.curX,self.curY]+args))
		a,b,self.lastcX,self.lastcY,self.curX,self.curY=args
		ln = bz.tolines(self.precision)
		for l in ln:
			self._lin(l.p2.x,l.p2.y)
		
		
	def defaultShape(self,attrs,end=False):
		if end: return
		pass
	
	def __getitem__(self,itemname):
		if itemname in self.funcmap:
			return self.funcmap[itemname]
		else:
			return self.defaultShape
	
	def _hor(self,x):
		self.lines.append({"cmd":"H","args":(x) })
	def _ver(self,y):
		self.lines.append({"cmd":"V","args":(y) })
	def _mov(self,x,y):
		self.lines.append({"cmd":"M","args":(x,y) })
	def _lin(self,x,y):
		self.lines.append({"cmd":"L","args":(x,y) })
		



	def parse_d(self,d):
		d = re.sub("[\t\r\n]",'',d)
		ret=[]
		res = re.findall("([MZLHVCSmzlhvcs]{1})([-.,0-9]*)",d)
		for cmd,b in res:
			ret.append({"cmd":cmd,"args":self.parse_nums(b)})
		return ret
	
	def parse_nums(self,s):
		ret = []
		res = re.findall("(-?[.0-9]+,?)",s)
		prevpar = ","
		for num in res:
			num = eval(num)
			if type(num) is TupleType:
				num=num[0]
			ret.append(num*unit)
		return ret
	


unit = Metrics.pixel


