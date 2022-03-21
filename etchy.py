from email.policy import default
from turtle import Turtle, Screen
from PIL import ImageGrab
import csv
from webbrowser import get
import click
import os
from tqdm import tqdm

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
    # Resize canvas if turtle went off screen
    x, y = turtle.pos()

    w, h = screen.screensize()
    sw = screen.getcanvas().winfo_width()
    sh = screen.getcanvas().winfo_height()
    canvas = screen.getcanvas()
    if not (-(w/2 - sw/2) < x < (w/2 - sw/2)):
        w *= 2
        h *= 2
        screen.screensize(w, h)
    if not (-(h/2 - sh/2) < y < (h/2 - sh/2)):
        w *= 2
        h *= 2
        screen.screensize(w, h)
    # Keep the turtle in the center of the screen at all time 
    # (something fucked up happens to turtle coordinate and they are double what they should be)
    # (so i divide them by 2 and IT JUST WORKS OK.)
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
    
    if commands != []:
        # Parse and execute every command using correct parser
        etchy.screen.colormode(255)
        for command in tqdm(commands):
            execute_command(etchy.turtle, etchy.screen, command, parser)
        if outputfile is not None:
            # Get final canvas dimension
            w, h = etchy.screen.screensize()
            click.echo(f"W:{w} H:{h}")
            canvas = etchy.screen.getcanvas()
            x = -w//2
            y = -h//2
            click.echo(f"Output Start W: {x} H:{y}")
            click.echo(f"Output End   W: {x+w} H:{y+h}")
            etchy.screen.update()
            canvas.postscript(file=outputfile, x=x, y=y, width=w, height=h)
    etchy.screen.mainloop()


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