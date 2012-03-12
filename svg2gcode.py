#/usr/bin/python

import sys, os,re
from types import *
from SVG import GMaker
from xml.parsers.expat import ParserCreate
import pprint
from geometry import *

if (len(sys.argv) < 2):
	print "no file specified"
	print "usage: <code>python svg2gcode.py <svg-to-process></code>"
	exit()

try :
	f = open( sys.argv[1],'r')
except:
	print "error opening file",sys.argv[1]
	exit()


#b = CubicBezier(Point(0,0),Point(0,1),Point(1,0),Point(1,1))
#print b.length()
#print b.tolines(Metrics.mm/2)
#exit()

# parse input file
p = ParserCreate()
interpreter = GMaker(precision=Metrics.mm)

p.StartElementHandler  = interpreter.startElement
p.EndElementHandler    = interpreter.endElement
p.CharacterDataHandler = interpreter.characterData
p.ParseFile(f)


o=open(sys.argv[1]+".gcode",'w')
o.write(interpreter.getDrawingCode())
o.close()

#svg = 

exit()
