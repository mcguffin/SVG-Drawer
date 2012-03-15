#/usr/bin/python

import sys, os,re
from types import *
from SVG import SVGRenderer
from GMaker import GMaker
import pprint
from geometry import *
import math

if (len(sys.argv) < 2):
	print "no file specified"
	print "usage: <code>python svg2gcode.py <svg-to-process></code>"
	exit()

try :
	f = open( sys.argv[1],'r')
except:
	print "error opening file",sys.argv[1]
	exit()


'''
#b = QuadraticBezier(Point(2,3),Point(2,4),Point(3,4))
#print b.length()
#print b.tolines(Metrics.mm/4)
#exit()

#g =  LinearEquation.fromAngleIntercept(math.pi*0.25,1)
#print "g", g
#print g.getX(12)

f = Polygon()
f.addPoint(Point(0,0))
f.addPoint(Point(10,1))
f.addPoint(Point(8,6))
f.addPoint(Point(-2,4))

pprint.pprint( f.getHatching(math.pi*0.25,1))

#if g.intersects(l):
#	print g.intersectionWith(l)

'''


# parse input file
interpreter = SVGRenderer(precision=Metrics.mm*0.5)
interpreter.parseFile(f)

outfile = sys.argv[1]+".gcode"
o=open(outfile,'w')
o.write(GMaker(interpreter).getDrawingCode())
o.close()

print "Saved gcode to %s" % outfile
print "Done!"

#svg = 

exit()
