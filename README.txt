SVG-Drawer
==========
(svg2gcode utility)

Generates GCode for drawing SVG Shapes.
(see also http://www.thingiverse.com/thing:19038)

It currently understands the SVG-Tags
	RECT, CIRCLE, ELLIPSE, LINE, POLYLINE, POLYGON, PATH

For PATH-elements there is only limited support, as it does not parse quadratic bezier curves and arcs.






To-Do:
- PATH: Q,q,T,t (Quadratic bezier)
		A,a		(Arcs)
- Core: Odd behavior at 0° and 90° angles
- UI: Realign UI at window resizing
