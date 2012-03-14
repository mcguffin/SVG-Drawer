from SVG import LinearMoves
import math
from geometry import Point
class GMaker:
	liftZ = 5
	endZ = 30
	offsetZ = 6.9
	feedrate = 480
	
	def __init__(self,data):
		if not isinstance(data, LinearMoves):
			raise TypeError("'data' is not of type LinearMoves")
		self.data = data
	
		
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
			
			
			
			lines = form.getLines()
			
			coord = ((lines[0].p0*t1)+t2).value()
			G+="G1 Z%d ; lift Z\n" % (self.liftZ+self.offsetZ)
			G+="G1 X%f Y%f\n" % coord
			G+="G1 Z%d ; return Z\n" % self.offsetZ
			
			for l in lines:
				G+="G1 X%f Y%f\n" % ((l.pn*t1)+t2).value()
			
			
			angles = [math.pi*0.125,math.pi*0.25,math.pi*0.375,math.pi*0.5,math.pi*0.625,math.pi*0.75]
			
			for angle in angles:
				odd = False
				for f in form.getHatching(angle,2):
					if odd: f = f.reverse()
					coord = ((f.p0*t1)+t2).value()
					G+="G1 Z%d ; lift Z\n" % (self.liftZ+self.offsetZ)
					G+="G1 X%f Y%f\n" % coord
					G+="G1 Z%d ; return Z\n" % self.offsetZ
					G+="G1 X%f Y%f\n" % ((f.pn*t1)+t2).value()
					odd = not odd
				
		G+="G1 Z%d\n"%self.endZ
		#print G
		return G
	
	def getMillingCode(self):
		# for future use
		pass
