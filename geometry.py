import math
from bezmisc import bezierlength,beziersplitatt


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
	"""Represents a Point in 3D-Space"""
	x=0
	y=0
	z=0
	
	def __init__(self,x=0,y=0,z=0):
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)
	
	def crossProduct(self,other):
		return Point(self.y*other.z - self.z*other.y, self.z*other.x - self.x*other.z, self.x*other.y - self.y*other.x);
	
	def distance2D(self,other):
		p = (self-other)
		return math.sqrt(p.x*p.x+p.y*p.y)
	
	def __add__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x + other.x, self.y + other.y, self.z + other.z)
		else:
			p=Point(self.x + other, self.y + other, self.z + other)
		return p

	def __sub__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x - other.x, self.y - other.y, self.z - other.z)
		else:
			p=Point(self.x - other, self.y - other, self.z - other)
		return p
	
	def __mul__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x * other.x, self.y * other.y, self.z * other.z)
		else:
			p=Point(self.x * other, self.y * other, self.z * other)
		return p
	
	def __div__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x / other.x, self.y / other.y, self.z / other.z)
		else:
			p=Point(self.x / other, self.y / other, self.z / other)
		return p
	
	def __floordiv__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x // other.x, self.y // other.y, self.z // other.z)
		else:
			p=Point(self.x // other, self.y // other, self.z // other)
		return p
		
	def __mod__(self,other):
		if other.__class__ == self.__class__:
			p=Point(self.x % other.x, self.y % other.y, self.z % other.z)
		else:
			p=Point(self.x % other, self.y % other, self.z % other)
		return p


	def __str__(self):
		return "(Point: x=%s y=%s z=%s)" % (self.x,self.y,self.z)

	def __repr__(self):
		return "Point(%s,%s,%s)" % (self.x,self.y,self.z)


class Line:
	"""represents a line in coordinate space"""
	p1=Point()
	p2=Point()
	
	def __init__(self,p1,p2):
		self.p1=p1
		self.p2=p2
		
	def getVector(self):
		return self.p2-self.p1
		
	def crossProduct(self,other):
		return self.getVector().crossProduct(other.getVector())
		
	def getCenter(self):
		return self.p1 + (self.p2-self.p1)*0.5
	
	def length(self):
		return self.p1.distance2D(self.p2)
	
	def __add__(self,other):
		if other.__class__ == self.__class__:
			l=Line(self.p1 + other.p1, self.p2 + other.p2)
		else:
			l=Line(self.p1 + other, self.p2 + other)
		return l

	def __sub__(self,otherPoint):
		if other.__class__ == self.__class__:
			l=Line(self.p1 - other.p1, self.p2 - other.p2)
		else:
			l=Line(self.p1 - other, self.p2 - other)
		return l
	
	def __mul__(self,other):
		if other.__class__ == self.__class__:
			l=Line(self.p1 * other.p1, self.p2 * other.p2)
		else:
			l=Line(self.p1 * other, self.p2 * other)
		return l
	
	def __div__(self,other):
		if other.__class__ == self.__class__:
			l=Line(self.p1 / other.p1, self.p2 / other.p2)
		else:
			l=Line(self.p1 / other, self.p2 / other)
		return l
	
	def __floordiv__(self,other):
		if other.__class__ == self.__class__:
			l=Line(self.p1 // other.p1, self.p2 // other.p2, self.z // other.z)
		else:
			l=Line(self.p1 // other, self.p2 // other, self.z // other)
		return l
		
	def __mod__(self,other):
		if other.__class__ == self.__class__:
			l=Line(self.p1 % other.p1, self.p2 % other.p2, self.z % other.z)
		else:
			l=Line(self.p1 % other, self.p2 % other, self.z % other)
		return l

	def __str__(self):
		return "(Line: p1=%s y=%s)" % (self.p1,self.p2)

	def __repr__(self):
		return "Line(%s,%s)" % (repr(self.p1),repr(self.p2))

class QuadraticBezier:
	p1=Point() # start
	p2=Point() # control
	p3=Point() # end
	
	def __init__(self,p1,p2,p3):
		self.p1=p1
		self.p2=p2
		self.p3=p3

class CubicBezier:
	p1=Point() # start
	p2=Point() # control 1
	p3=Point() # control 2
	p4=Point() # end
	
	@classmethod
	def fromCoords(cls,x1,y1,x2,y2,x3,y3,x4,y4):
		return CubicBezier(Point(x1,y1),Point(x2,y2),Point(x3,y3),Point(x4,y4))
	
	def __init__(self,p1,p2,p3,p4):
		self.p1=p1
		self.p2=p2
		self.p3=p3
		self.p4=p4
	
	def length(self):
		return bezierlength(((self.p1.x,self.p1.y),(self.p2.x,self.p2.y),(self.p3.x,self.p3.y),(self.p4.x,self.p4.y)))

	def split(self):
		(((p1x,p1y),(p2x,p2y),(p3x,p3y),(p4x,p4y)), ((q1x,q1y),(q2x,q2y),(q3x,q3y),(q4x,q4y))) = beziersplitatt( ((self.p1.x,self.p1.y), (self.p2.x,self.p2.y),(self.p3.x,self.p3.y),(self.p4.x,self.p4.y)), 0.5)
		return CubicBezier.fromCoords(p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y),CubicBezier.fromCoords(q1x,q1y,q2x,q2y,q3x,q3y,q4x,q4y)
	
	def tolines(self,precision=Metrics.mm):
		segments = [self]
		while (segments[0].toflat().length() > precision):
			print segments[0].toflat().length(),precision
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
		
	def toflat(self):
		return Line(self.p1,self.p4)
		
	def __str__(self):
		return "(CubicBezier p1=%s, p2=%s, p4=%s, p4=%s)" % (self.p1,self.p2,self.p3,self.p4)

	def __repr__(self):
		return "CubicBezier(%s,%s,%s,%s)" % (repr(self.p1),repr(self.p2),repr(self.p3),repr(self.p4))

'''
float blen(v* p0, v* p1, v* p2)
{
v a,b;
a.x = p0->x - 2*p1->x + p2->x;
a.y = p0->y - 2*p1->y + p2->y;
b.x = 2*p1->x - 2*p0->x;
b.y = 2*p1->y - 2*p0->y;
float A = 4*(a.x*a.x + a.y*a.y);
float B = 4*(a.x*b.x + a.y*b.y);
float C = b.x*b.x + b.y*b.y;

float Sabc = 2*sqrt(A+B+C);
float A_2 = sqrt(A);
float A_32 = 2*A*A_2;
float C_2 = 2*sqrt(C);
float BA = B/A_2;

return ( A_32*Sabc + A_2*B*(Sabc-C_2) + (4*C*A-B*B)*log( (2*A_2+BA+Sabc)/(BA+C_2) ) )/(4*A_32);
};'''

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

		