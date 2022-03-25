from math import ceil
from turtle import Turtle, Screen
import csv
import click
import os
from tqdm import tqdm

SAFETY_MARGIN = 50

def parse_csv_command(turtle, command):
    match [command[0:2],command[2:]]:
        case ["FW", distance]:
            turtle.forward(float(distance))
        case ["LR", angle]:
            turtle.left(float(angle))
        case ["RR", angle]:
            turtle.right(float(angle))

def parse_tcode_command(turtle, command):
    match command.split():
        case ["FORWARD", distance]:
            turtle.forward(float(distance))
        case ["BACKWARD", distance]:
            turtle.backward(float(distance))
        case ["LEFT", distance]:
            # Strafe left (turn left by 90˚ left than move forward and then turn back 90˚ to the right)
            turtle.degrees()
            turtle.left(90)
            turtle.forward(float(distance))
            turtle.right(90)
        case ["RIGHT", distance]:
            # Strafe right (turn right by 90˚ than move forward and then turn back 90˚ to the left)
            turtle.degrees()
            turtle.right(90)
            turtle.forward(float(distance))
            turtle.left(90)
        case ["ROTATE_L", angle]:
            turtle.radians()
            turtle.left(float(angle))
        case ["ROTATE_R", angle]:
            turtle.radians()
            turtle.right(float(angle))
        case ["ROTATE_LD", angle]:
            turtle.degrees()
            turtle.left(float(angle))
        case ["ROTATE_RD", angle]:
            turtle.degrees()
            turtle.right(float(angle))
        case ["SETHEADING", angle]:
            turtle.radians()
            turtle.setheading(float(angle))
        case ["SETHEADING_D", angle]:
            turtle.degrees()
            turtle.setheading(float(angle))
        case ["PENUP"]:
            turtle.penup()
        case ["PENDOWN"]:
            turtle.pendown()
        case ["COLOR", *color]:
            if color[0] == "#":
                turtle.pencolor(color)
            else:
                r, g, b = [int(c.strip(',')) for c in color]
                turtle.pencolor((r, g, b))
        case ["THICKNESS", thickness]:
            turtle.pensize(float(thickness))

def execute_command(turtle : Turtle, screen : Screen, command, parser):
    match parser:
        case "CSV":
            parse_csv_command(turtle, command)
        case "TCODE":
            parse_tcode_command(turtle, command)
    # Resize canvas if turtle went off screen (keep it square for later EPS export, breaks otherwise)
    x, y = turtle.pos()
    w, h = screen.screensize()
    sw = screen.getcanvas().winfo_width()
    sh = screen.getcanvas().winfo_height()
    canvas = screen.getcanvas()
    if not (-(w/2 - sw/2) < x//2 < (w/2 - sw/2)):
        w *= 2
        h *= 2
        screen.screensize(w, h)
    if not (-(h/2 - sh/2) < y//2 < (h/2 - sh/2)):
        w *= 2
        h *= 2
        screen.screensize(w, h)
    # Keep the turtle in the center of the screen at all time 
    # (something fucked up happens to the turtle coordinates and they are double what they should be)
    # (so I divide them by 2 and IT JUST WORKS OK.)
    canvas.xview_moveto(((x//2)+w//2 - sw/2)/w)
    canvas.yview_moveto((-(y//2)+h//2 - sh/2)/h)
    

@click.command()
@click.option('--inputfile', help='Name of the file to use as an input.')
@click.option('--outputfile', help='Name of the file to use as the output.')
@click.option('--parser', default="CSV", prompt='Which parser do you want to use on the file CSV/TCODE?',
            help='Selects a parser between CSV and TCODE to decode the instruction in the file provided')
def etchy_cli(inputfile, outputfile, parser):
    """CLI interface for Etchy"""
    if not os.path.isfile(inputfile):
        click.echo(click.style('File not found!', fg='red'))
        return
    parser = parser.upper()
    if parser not in {"CSV", "TCODE"}:
        click.echo(click.style('Parser does not exist.', fg='red'))
        return

    # Create Etchy instance
    etchy = Etchy()
    commands = []
    parsed_commands = []

    match parser:
        case "CSV":
            with open(inputfile, newline='') as csvfile:
                # Automatically detect the formatting of the CSV file
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                #Check that the found delimiter makes sense:
                if dialect.delimiter not in ",;/: \r\n":
                    # Most likely the file is a single column with no delimiter
                    dialect.delimiter = "\n"
                # Seek back to the beginning of the file
                csvfile.seek(0)
                # Read the entire CSV file and split it in it's individual command
                spamreader = csv.reader(csvfile, dialect)
                for row in spamreader:
                    for command in row:
                        commands.append(command)
        case "TCODE":
            with open(inputfile) as tcodefile:
                for command in tcodefile:
                    commands.append(command.strip())
    
    # Keep track of where etchy has gone to create correct bounding box later
    bbox_detail = {"blx": 0, "bly": 0, "trx": 0, "try": 0}
    # FOR TESTING ONLY, CONSUMES HUGE AMOUNT OF MEMORY FOR NOTHING
    x_pos = []
    y_pos = []
    if commands != []:
        # Parse and execute every command using correct parser
        etchy.screen.colormode(255)
        for command in tqdm(commands):
            execute_command(etchy.turtle, etchy.screen, command, parser)
            x, y = etchy.turtle.pos()
            x_pos.append(x)
            y_pos.append(y)
            if x//2 < bbox_detail["blx"]:
                bbox_detail["blx"] = x//2
            elif x//2 > bbox_detail["trx"]:
                bbox_detail["trx"] = x//2
            if y//2 < bbox_detail["bly"]:
                bbox_detail["bly"] = y//2
            elif y//2 > bbox_detail["try"]:
                bbox_detail["try"] = y//2
        if outputfile is not None:
            # Get final canvas dimension
            w, h = etchy.screen.screensize()
            click.echo(f"W:{w} H:{h}")
            canvas = etchy.screen.getcanvas()
            x = -w/2
            y = -h/2
            click.echo(f"Output Start W: {x} H:{y}")
            click.echo(f"Output End   W: {x+w} H:{y+h}")
            canvas_t = etchy.turtle.getscreen().getcanvas()
            etchy.turtle.getscreen().update()
            #canvas_t.postscript(file=outputfile, x=-w//2, y=-h//2, width=w, height=h, pageheight=h, pagewidth=w)
            x_min, y_min, x_max, y_max = min(x_pos)/2, min(y_pos)/2, max(x_pos)/2, max(y_pos)/2
            x_min_r, y_min_r, x_max_r, y_max_r = [v * 0.05 for v in [x_min, y_min, x_max, y_max]]
            canvas_t.postscript(file=outputfile, x=x, y=y, width=w, height=h)
            print(bbox_detail["trx"]-bbox_detail["blx"])
            print(bbox_detail["try"]-bbox_detail["bly"])
            click.echo(f"BBOX NOT SCALED: {min(x_pos)//2:.2f} {min(y_pos)//2:.2f} {max(x_pos)//2:.2f} {max(y_pos)//2:.2f}")
            click.echo(f"BBOX : {bbox_detail['blx'] * 0.05:.2f} {bbox_detail['bly'] * 0.05:.2f} {bbox_detail['trx'] * 0.05:.2f} {bbox_detail['try'] * 0.05:.2f}")
            # Write bbox to an output file for later use with pdfcrop
            bbox_str = f"{ceil((w*0.05)/2+x_min_r)-SAFETY_MARGIN} {ceil((h*0.05)/2+y_min_r)-SAFETY_MARGIN} {ceil((w*0.05)/2+x_min_r + (x_max_r - x_min_r))+SAFETY_MARGIN} {ceil((h*0.05)/2+y_min_r + (y_max_r - y_min_r))+SAFETY_MARGIN}"
            with open("bbox_tmp.txt", "w") as f:
                f.write(bbox_str)
            with open("bbox_list.txt", "a") as f:
                f.write(bbox_str + '\n')
    #etchy.screen.mainloop()


class Etchy():
    def __init__(self) -> None:
        # Create the turtle and the screen it will live on
        self.screen = Screen()
        self.screen.setup(600, 600)
        self.screen.setworldcoordinates(-580, -580, 580, 580)
        self.turtle = Turtle()
        self.turtle.speed(0)
        self.screen.tracer(1000, 0)
        # Set up some control for the turtle window
        self.canvas = self.screen.getcanvas()
        self.canvas.bind("<MouseWheel>", self.zoom_canvas)
        self.canvas.bind("<ButtonPress-1>", self.move_canvas_start)
        self.canvas.bind("<B1-Motion>", self.move_canvas)

    def zoom_canvas(self, event):
        if (event.delta > 0):
            self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        elif (event.delta < 0):
            self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))

    def move_canvas_start(self, event):
        self.canvas.scan_mark(event.x, event.y)
        print(f"Click at {self.canvas.canvasx(event.x)},{self.canvas.canvasy(event.y)}\n")

    def move_canvas(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

if __name__ == "__main__":
    etchy_cli()