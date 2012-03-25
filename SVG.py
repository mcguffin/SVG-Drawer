import re
from xml.parsers.expat import ParserCreate
from types import *
from pprint import pprint
from geometry import Metrics,CubicBezier,Point,Form,Polygon
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

class LinearMoves:
	lines=[]
	
	def getLines(self):
		return self.lines

class SVGRenderer(LinearMoves):
	
	funcmap={}
	nodeNames = ["rect","circle","ellipse","line","polyline","polygon","path","svg"]
	
	def __init__(self,precision=Metrics.mm):
		# create functions to be called from svg-nodes
		for nn in self.nodeNames:
			self.funcmap[nn]= eval('self.'+nn)
			
		self.precision = precision
		self.forms = []
		pass
	
	def reduce_color(self,color):
		n = eval('0x'+color.replace('#',''))
		b = n%256
		g = (n>>8)%256
		r = (n>>16)%256
		return 255-(r+g+b)/3
		
	def drawing_attrs(self,attrs):
		bwidth = 1
		bcolor = 0
		fill = 255
		if "fill" in attrs:
			fill = self.reduce_color(attrs["fill"])
			
		if "stroke" in attrs:
			bcolor = self.reduce_color(attrs["stroke"])
			if "stroke-width" in attrs:
				bwidth = attrs["stroke-width"]
				
		return (bwidth,bcolor),fill
	
	def parseFile(self,f):
		p = ParserCreate()
		p.StartElementHandler  = self.startElement
		p.EndElementHandler    = self.endElement
		p.CharacterDataHandler = self.characterData
		p.ParseFile(f)
		
	
	def startElement(self,name,attrs):
		self[name](attrs)
		pass

	def endElement(self,name):
		self[name](None,end=True)
		pass

	def characterData(self,data):
		# don't care
		pass

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
		self._form(Polygon(*self.drawing_attrs(attrs)))
		r = float(attrs["r"])*unit
		x = float(attrs["cx"])*unit
		y = float(attrs["cy"])*unit
		
		attrs["rx"] = attrs["ry"] = attrs["r"]
		return self.ellipse(attrs)
		
	def ellipse(self,attrs,end=False):
		if end: return
		self._form(Polygon(*self.drawing_attrs(attrs)))
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
		#print attrs
		self._form(Polygon(*self.drawing_attrs(attrs)))
		x=self.curX=float(attrs["x"])*unit
		y=self.curY=float(attrs["y"])*unit
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
		self._form(Form(*self.drawing_attrs(attrs)))
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
		self._form(Form(*self.drawing_attrs(attrs)))
		points = attrs["points"].split()
		x,y = eval("("+points[0]+")")
		self._mov(x*unit,y*unit)
		for p in points:
			x,y = eval("("+p+")")
			self._lin(x*unit,y*unit)
		return points
		
	def polygon(self,attrs,end=False):
		if end: return
		self._form(Polygon(*self.drawing_attrs(attrs)))
		points = self.polyline(attrs)
		# close
		x,y = eval("("+points[0]+")")
		self._lin(x*unit,y*unit)
		
	def path(self,attrs,end=False):
		if end: return
		self.curX = self.curY = 0
		commands = self.parse_d(attrs["d"])
		self._form(Polygon(*self.drawing_attrs(attrs)))
		for cm in commands:
			cmd = cm["cmd"]
			args = cm["args"]
			if cmd=='M':
				self._mov(args[0],args[1])
			elif cmd=='m':
				self._mov(self.curX+args[0],self.curY+args[1])
			elif cmd=='L':
				self._lin(args[0],args[1])
			elif cmd=='l':
				self._lin(self.curX+args[0],self.curY+args[1])
			elif cmd=='H':
				self._hor(args[0])
			elif cmd=='h':
				self._hor(self.curX+args[0])
			elif cmd=='V':
				self._ver(args[0])
			elif cmd=='v':
				self._ver(self.curY+args[0])
			
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
				self._cls()
				pass
			elif cmd=="z":
				pass
				
			# c,C,s,S,z,Z,q,Q,t,T,a,A
		
		pass
	
	def bezier(self,args):
		bz=CubicBezier.fromCoords(*([self.curX,self.curY]+args))
		a,b,self.lastcX,self.lastcY,self.curX,self.curY=args
		ln = bz.tolines(self.precision)
		for l in ln:
			self._lin(l.pn.x,l.pn.y)
		
		
	def defaultShape(self,attrs,end=False):
		if end: return
		pass
	
	def __getitem__(self,itemname):
		if itemname in self.funcmap:
			return self.funcmap[itemname]
		else:
			return self.defaultShape
	
	# reduced commands
	def _form(self,form):
		self.forms.append(form)
	def _mov(self,x,y):
		# = begin shape
		self.forms[len(self.forms)-1].addPoint(Point(x,y),'move')
		self.curX=x
		self.curY=y
	def _hor(self,x):
		self.forms[len(self.forms)-1].addPoint(Point(x,self.curY))
		self.curX=x
	def _ver(self,y):
		self.forms[len(self.forms)-1].addPoint(Point(self.curX,y))
		self.curY=y
	def _lin(self,x,y):
		self.forms[len(self.forms)-1].addPoint(Point(x,y))
		self.curX=x
		self.curY=y
	def _cls(self):
		p0 = self.forms[len(self.forms)-1].points[0]
		self.forms[len(self.forms)-1].addPoint(Point(p0.x,p0.y))



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


