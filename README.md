# Etchy
An interactive drawing program that can read different file format to draw
lines of different color and thickness using the turle Python library.

## Supported file types:
### .CSV
List of valid commands:
- LXYZ (move forward by XYZ)
- AXYZ (rotate by an XYZ in degree or radians depending on import settings)

### .TCODE (aka Turtle Code)
List of valid commands:
- `FORWARD XYZ` (move forward by XYZ)
- `BACKWARD XYZ` (move backward by XYZ)
- `LEFT XYZ` (strafe left by XYZ)
- `RIGHT XYZ` (strafe right by XYZ)
- `ROTATE XYZ` (rotate by XYZ radians)
- `ROTATE_D XYZ` (rotate by XYZ degrees)
- `COLOR R,G,B` (set the color of the streak in RGB8 mode)
- THICKNESS XYZ (set the thickness of the streak to XYZ pixels)
