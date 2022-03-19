# Etchy
An interactive drawing program that can read different file format to draw
lines of different color and thickness using the turle Python library.

## Supported file types:
### .CSV (meant for monochrome use only)
List of valid commands:
- `FWXYZ` (move forward by XYZ)
- `LRXYZ` (rotate left by an XYZ in degree or radians depending on import settings)
- `RRXYZ` (rotate right by an XYZ in degree or radians depending on import settings)

### .TCODE (aka Turtle Code, unlocks the full potential of the program)
List of valid commands:
- `FORWARD XYZ` (move forward by XYZ)
- `BACKWARD XYZ` (move backward by XYZ)
- `LEFT XYZ` (strafe left by XYZ)
- `RIGHT XYZ` (strafe right by XYZ)
- `ROTATE_L XYZ` (rotate left by XYZ radians)
- `ROTATE_R XYZ` (rotate right by XYZ radians)
- `ROTATE_LD XYZ` (rotate left by XYZ degrees)
- `ROTATE_RD XYZ` (rotate right by XYZ degrees)
- `COLOR R,G,B` (set the color of the streak in RGB8 mode)
- `THICKNESS XYZ` (set the thickness of the streak to XYZ pixels)
- `PENUP` (lift the pen up to stop drawing while moving)
- `PENDOWN` (puts the pen down to resume drawing while moving)
- `SETHEADING XYZ` (set the heading of the turtle to XYZ radians)
- `SETHEADING_D XYZ` (set heading of the turtle to XYZ degrees)
