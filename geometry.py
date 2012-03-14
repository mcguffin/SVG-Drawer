import math
from bezmisc import bezierlength,beziersplitatt
from pprint import pprint

class Metrics:
	mu=0.001
	mm=1.0
	cm=mm*10
	dm=cm*10
	m=dm*10
	km=m*1000
	inch=mm*25.4
	pixel=inch/72





class Point:
	"""Represents a Point in 2D"""
	x=0
	y=0
	
	@classmethod
	def fromPolar(cls,len,angle):
		return Point(len*math.cos(angle),len*math.sin(angle))
	
	def __init__(self,x=0,y=0):
		self.x = float(x)
		self.y = float(y)
	
	def getDistance(self,other):
		p = self - other
		return p.length()
	
	def rotate(self,angle):
		d = self.length()
		if self.y>0:
			pAngle = math.acos(self.x/d)
		else :
			pAngle = -math.acos(self.x/d)
		return Point.fromPolar(d, self.pAngle+angle)
		
	# more like a vector...
	def normalize(self,length=1):
		return Point.fromPolar(length,self.getAngle())
	
	def getAngle(self):
		d = self.length()
		if self.y>0:
			return math.acos(self.x/d)
		else :
			return -math.acos(self.x/d)
			
	def length(self):
		# should implement length^2 as well for faster comparision
		return math.sqrt(self.length2())
	
	def length2(self):
		return self.x*self.x+self.y*self.y
	
	def value(self):
		return self.x,self.y
	
	def __add__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x + other.x, self.y + other.y)
		else:
			p=Point(self.x + other, self.y + other)
		return p

	def __sub__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x - other.x, self.y - other.y)
		else:
			p=Point(self.x - other, self.y - other)
		return p
	
	def __mul__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x * other.x, self.y * other.y)
		else:
			p=Point(self.x * other, self.y * other)
		return p
	
	def __div__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x / other.x, self.y / other.y)
		else:
			p=Point(self.x / other, self.y / other)
		return p
	
	def __floordiv__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x // other.x, self.y // other.y)
		else:
			p=Point(self.x // other, self.y // other)
		return p
		
	def __mod__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x % other.x, self.y % other.y)
		else:
			p=Point(self.x % other, self.y % other)
		return p
	
	def __eq__(self,other):
		return self.x == other.y and self.y == other.y
	
	def __ne__(self,other):
		return other == None or self.x != other.y or self.y != other.y
	
	def __str__(self):
		return "(Point: x=%s y=%s)" % (self.x,self.y)

	def __repr__(self):
		return "Point(%s,%s)" % (self.x,self.y)


class Line:
	"""represents a line in coordinate space"""
	p0=Point()
	pn=Point()
	
	def __init__(self,p0,pn):
		if p0==pn:
			raise ValueError("p0 must differ from pn!")
		self.p0=p0
		self.pn=pn
		
	def getVector(self):
		return self.pn-self.p0
		
	def crossProduct(self,other):
		return self.getVector().crossProduct(other.getVector())
		
	def getCenter(self):
		return self.p0 + (self.pn-self.p0)*0.5
	
	def length(self):
		return self.p0.distance2D(self.pn)
	
	def reverse(self):
		return Line(self.pn,self.p0)
	
	def length(self):
		return (self.pn - self.p0).length()
	
	def length2(self):
		return (self.pn - self.p0).length2()
	
	
	def __add__(self,other):
		if other.__class__ == self.__class__:
			l=Line(self.p0 + other.p0, self.pn + other.pn)
		else:
			l=Line(self.p0 + other, self.pn + other)
		return l

	def __sub__(self,other):
		if other.__class__ == self.__class__:
			l=Line(self.p0 - other.p0, self.pn - other.pn)
		else:
			l=Line(self.p0 - other, self.pn - other)
		return l
	
	def __mul__(self,other):
		if other.__class__ == self.__class__:
			l=Line(self.p0 * other.p0, self.pn * other.pn)
		else:
			l=Line(self.p0 * other, self.pn * other)
		return l
	
	def __div__(self,other):
		if other.__class__ == self.__class__:
			l=Line(self.p0 / other.p0, self.pn / other.pn)
		else:
			l=Line(self.p0 / other, self.pn / other)
		return l
	
	def __floordiv__(self,other):
		if other.__class__ == self.__class__:
			l=Line(self.p0 // other.p0, self.pn // other.pn, self.z // other.z)
		else:
			l=Line(self.p0 // other, self.pn // other, self.z // other)
		return l
		
	def __mod__(self,other):
		if other.__class__ == self.__class__:
			l=Line(self.p0 % other.p0, self.pn % other.pn, self.z % other.z)
		else:
			l=Line(self.p0 % other, self.pn % other, self.z % other)
		return l

	def __eq__(self,other):
		return self.p0 == other.p0 and self.pn == other.pn
	
	def __ne__(self,other):
		return other == None or self.p0 != other.p0 or self.pn != other.pn
	
	def __str__(self):
		return "(Line: p0=%s pn=%s)" % (self.p0,self.pn)

	def __repr__(self):
		return "Line(%s,%s)" % (repr(self.p0),repr(self.pn))

class LinearEquation:
	#angle
	#intercept
	#transform x somehow

	# ortsvektor | pos
	# richtungsvektor | dis
	@classmethod
	def fromPointAngle(cls,point,angle):
		if angle == math.pi or angle == 0:
			slope = 0.0
			intercept = point.y
			x = None
		elif angle == math.pi*0.5:
			slope = float('inf')
			intercept = float('inf')
			x = point.x
		else:
			slope = math.tan(angle)
			intercept = point.y - slope*point.x # no good mon - deeze f*cken floats
			x = None
		return LinearEquation(slope,intercept,x)
	
	@classmethod
	def fromAngleIntercept(cls,angle,intercept=0):
		if angle == math.pi:
			slope = 0.0
		elif angle == math.pi*0.5:
			slope = float('inf')
		else:
			slope = math.tan(angle)
		return LinearEquation(slope,intercept)
	
	@classmethod
	def fromLine(cls,line):
		# careful with equal x's!
		if line.pn.x == line.p0.x:
			return LinearEquation(float('inf'),0,line.pn.x)
		slope = (line.pn.y - line.p0.y) / (line.pn.x - line.p0.x)
		intercept = line.pn.y - slope * line.pn.x
		
		#op = line.p0
		#pp = line.pn-line.p0
		#slope = pp.x/pp.y
		return LinearEquation(slope, intercept)
	
	def __init__(self,slope=1,intercept=0,x=None):
		#self.op = Point(0,intercept)
		#self.pp = Point(1,slope)
		#self.scalar = 1
		
		self.x = x
		self.a = slope
		self.b = intercept
	
	def getAngle(self):
		pass
	
	def getY(self, x):
		return self.a*x + self.b
		
	def getX(self,y):
		if self.x != None: return self.x
		return (y - self.b)/self.a
	
	def intersects(self,line):
		if not isinstance(line,Line):
			raise TypeError("'line' is not of type Line")
		
#		if self.a == float('inf'):
		a = self.getX(line.p0.y) < line.p0.x
		b = self.getX(line.pn.y) > line.pn.x
#		else :
#			a = self.getY(line.p0.x) <= line.p0.y
#			b = self.getY(line.pn.x) >= line.pn.y
		return a == b
		
	def intersectionWith(self,line):
		if not isinstance(line,Line):
			raise TypeError("'line' is not of type Line")
		p = Point()
		g = self.fromLine(line)
		p.x =  (g.b - self.b) / (self.a-g.a)
		p.y = g.getY(p.x)
		if math.isnan(p.y): p.y=self.getY(p.x)
		return p
		
	def __str__(self):
		if self.x != None: return "x = %s" % self.x
		return "f(x) = %s * x + %s" % (self.a, self.b)

class Bezier():
	p0=Point() # start
	pn=Point() # end
	
	def toflat(self):
		return Line(self.p0, self.pn)
	
	def tolines(self,precision=Metrics.mm):
		segments = [self]
		prec2 = precision*precision
		while (segments[0].toflat().length2() > prec2):
			segs2=[]
			for seg in segments:
				b1,b2 = seg.split()
				segs2.append(b1)
				segs2.append(b2)
			segments = segs2
		ret = []
		for seg in segments:
			ret.append(seg.toflat())
		return ret

class QuadraticBezier(Bezier):
	p0=Point() # start
	p1=Point() # control
	pn=Point() # end
	
	@classmethod
	def fromCoords(cls,x1,y1,x2,y2,x3,y3):
		return QuadraticBezier(Point(x1,y1),Point(x2,y2),Point(x3,y3))
		
	def __init__(self,p0,p1,pn):
		self.p0=p0
		self.p1=p1
		self.pn=pn
	
	def length(self):
		# found at and translated from: http://segfaultlabs.com/docs/quadratic-bezier-curve-length
		a = Point()
		b = Point()
		a.x = self.p0.x - 2*self.p1.x + self.pn.x
		a.y = self.p0.y - 2*self.p1.y + self.pn.y
		b.x = 2*self.p1.x - 2*self.p0.x
		b.y = 2*self.p1.y - 2*self.p0.y
		A = 4*(a.x*a.x + a.y*a.y)
		B = 4*(a.x*b.x + a.y*b.y)
		C = b.x*b.x + b.y*b.y
		
		Sabc = 2*math.sqrt(A+B+C)
		A_2 = math.sqrt(A)
		A_32 = 2*A*A_2
		C_2 = 2*math.sqrt(C)
		BA = B/A_2
		
		return ( A_32*Sabc + A_2*B*(Sabc-C_2) + (4*C*A-B*B)*math.log( (2*A_2+BA+Sabc)/(BA+C_2) ) )/(4*A_32)
	
	def split(self,t=0.5):
		a = self.p0 + (self.p1-self.p0)*t 
		b = self.pn - (self.pn-self.p1)*t 
		c = a + (a-b)*t
		return QuadraticBezier(self.p0,a,c), QuadraticBezier(c,b,self.pn)

	def toflat(self):
		return Line(self.p0,self.pn)
	
	
	def __str__(self):
		return "(CubicBezier p0=%s, p1=%s, pn=%s)" % (self.p0,self.p1,self.pn)

	def __repr__(self):
		return "QuadraticBezier(%s,%s,%s)" % (repr(self.p0),repr(self.p1),repr(self.pn))

class CubicBezier(Bezier):
	p0=Point() # start
	p1=Point() # control 1
	p2=Point() # control 2
	pn=Point() # end
	
	@classmethod
	def fromCoords(cls,x1,y1,x2,y2,x3,y3,x4,y4):
		return CubicBezier(Point(x1,y1),Point(x2,y2),Point(x3,y3),Point(x4,y4))
	
	def __init__(self,p0,p1,p2,pn):
		self.p0=p0
		self.p1=p1
		self.p2=p2
		self.pn=pn
	
	def length(self):
		return bezierlength(((self.p0.x,self.p0.y),(self.p1.x,self.p1.y),(self.p2.x,self.p2.y),(self.pn.x,self.pn.y)))

	def split(self,t=0.5):
		(((p0x,p0y),(p1x,p1y),(p2x,p2y),(pnx,pny)), ((q1x,q1y),(q2x,q2y),(q3x,q3y),(q4x,q4y))) = beziersplitatt( ((self.p0.x,self.p0.y), (self.p1.x,self.p1.y),(self.p2.x,self.p2.y),(self.pn.x,self.pn.y)), t)
		return CubicBezier.fromCoords(p0x,p0y,p1x,p1y,p2x,p2y,pnx,pny),CubicBezier.fromCoords(q1x,q1y,q2x,q2y,q3x,q3y,q4x,q4y)
	
	def tolines(self,precision=Metrics.mm):
		segments = [self]
		prec2 = precision*precision
		do_break=False
		while do_break==False:
			segs2=[]
			
			for seg in segments:
				if seg.toflat().length2() < prec2:
					segs2.append(seg)
					do_break = True
					continue
				do_break = False
				b1,b2 = seg.split()
				segs2.append(b1)
				segs2.append(b2)
			segments = segs2
		ret = []
		for seg in segments:
			ret.append(seg.toflat())
		return ret
		
	def toflat(self):
		return Line(self.p0,self.pn)
		
	def __str__(self):
		return "(CubicBezier p0=%s, p1=%s, p2=%s, pn=%s)" % (self.p0,self.p1,self.p2,self.pn)

	def __repr__(self):
		return "CubicBezier(%s,%s,%s,%s)" % (repr(self.p0),repr(self.p1),repr(self.p2),repr(self.pn))



class Form:
	
	def __init__(self):
		self.lines = None
		self.points=[]
		self.bounds = Line(Point(float('inf'),float('inf')),Point(-float('inf'),-float('inf')))
	
	
	def addPoint(self,point,type='draw'):
		if not isinstance(point,Point):
			raise TypeError("'point' is not of type Point")
		
		self.bounds.p0.x = min(point.x,self.bounds.p0.x)
		self.bounds.p0.y = min(point.y,self.bounds.p0.y)
		self.bounds.pn.x = max(point.x,self.bounds.pn.x)
		self.bounds.pn.y = max(point.y,self.bounds.pn.y)
		self.points.append((type,point))
	
	def getLines(self):
		if self.lines == None:
			prev = None
			self.lines = []
			for cmd,p in self.points:
				if prev != None and cmd == 'draw': 
					self.lines.append(Line(prev,p))
				prev = p
				
		return self.lines
		
	
class Polygon(Form):
	
	
	def getLines(self):
		if self.lines != None: return self.lines
		self.lines = Form.getLines(self)
		l = len(self.lines)
		
		self.lines.append(Line(self.lines[l-1].pn,self.lines[0].p0))
		return self.lines
	
	# always closed!
	def getHatching(self,angle,distance):
		# get bounds accoring to angle
		angle = angle%math.pi
		
		if angle > math.pi/2:
			p = self.bounds.p0
			test = self.bounds
		else:
			p = Point(self.bounds.pn.x, self.bounds.p0.y)
			test = Line(p,Point(self.bounds.p0.x, self.bounds.pn.y))
		vector = Point.fromPolar(distance,angle+math.pi*0.5)
		#print p,test, vector
		pts = []
		while 1:
			# make new LinearEquation
			ls = LinearEquation.fromPointAngle(p+vector*0.5,angle)
			if not ls.intersects(test): break
			pts.append([])
			for l in self.getLines():
				if ls.intersects(l):
					# find intersection, add point
					pts[len(pts)-1].append(ls.intersectionWith(l))
					pass
			# edit pts[len(pts)-1]: delete duplicates, sot by x,y
			p += vector
		lines = []
		# we are still too overtrustful...
		for plist in pts:
			for i in range(0,len(plist),2):
				lines.append(Line(plist[i],plist[i+1]))
		return lines
	

class Triangle:
	p1=Point()
	p2=Point()
	p3=Point()
	def __init__(self,p1,p2,p3):
		self.p1=p1
		self.p2=p2
		self.p3=p3
	
	def getNormal(self):
		return Line(self.p1,self.p2).crossProduct(Line(self.p2,self.p3))
		
	def __str__(self):
		return "(Triangle: x=%s y=%s z=%s)" % (self.p1,self.p2,self.p3)

	def __repr__(self):
		return "Triangle(%s,%s,%s)" % (repr(self.p1),repr(self.p2),repr(self.p3))

		