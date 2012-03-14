SVG-Drawer
==========
(svg2gcode utility)

Generates GCode for drawing SVG Shapes.
(see also http://www.thingiverse.com/thing:19038)


It currently understands these SVG-Tags:
RECT
CIRCLE
ELLIPSE
LINE
POLYLINE
POLYGON
PATH	(limited support)

Usage: python svg2gcode.py <some-svg-file>



To-Do:
- PATH: Q,q,T,t (Quadratic bezier)
		A,a		(Arc)
- Hatch fill
- Option: Ignore Paths with no fill and no stroke
- make different gcodes from different stroke-widths / -colors

- separate internal data model from GCode generator