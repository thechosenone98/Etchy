from email.policy import default
from turtle import *
import csv
import click
import os

def parse_csv_command(command):
    match [command[0:2],command[2:]]:
        case ["FW", distance]:
            forward(float(distance))
        case ["LR", angle]:
            left(float(angle))
        case ["RR", angle]:
            right(float(angle))

def parse_tcode_command(command):
    match command.split():
        case ["FORWARD", distance]:
            forward(float(distance))
        case ["BACKWARD", distance]:
            backward(float(distance))
        case ["LEFT", distance]:
            # Strafe left (turn left by 90˚ left than move forward and then turn back 90˚ to the right)
            degrees()
            left(90)
            forward(float(distance))
            right(90)
        case ["RIGHT", distance]:
            # Strafe right (turn right by 90˚ than move forward and then turn back 90˚ to the left)
            degrees()
            right(90)
            forward(float(distance))
            left(90)
        case ["ROTATE_L", angle]:
            radians()
            left(float(angle))
        case ["ROTATE_R", angle]:
            radians()
            right(float(angle))
        case ["ROTATE_LD", angle]:
            degrees()
            left(float(angle))
        case ["ROTATE_RD", angle]:
            degrees()
            right(float(angle))
        case ["COLOR", color]:
            if color[0] == "#":
                pencolor(color)
            else:
                r, g, b = [int(c.strip()) for c in color.split(",")]
                pencolor((r, g, b))
        case ["THICKNESS", thickness]:
            pensize(float(thickness))

def execute_command(command, parser):
    match parser:
        case "CSV":
            parse_csv_command(command)
        case "TCODE":
            parse_tcode_command(command)


@click.command()
@click.option('--inputfile', help='Name of the file to use as an input.')
@click.option('--parser', default="CSV", prompt='Which parser do you want to use on the file CSV/TCODE?',
              help='Selects a parser between CSV and TCODE to decode the instruction in the file provided')
def etchy_cli(inputfile, parser):
    """CLI interface for Etchy"""
    if not os.path.isfile(inputfile):
        click.echo(click.style('File not found!', fg='red'))
        return
    parser = parser.upper()
    if parser not in {"CSV", "TCODE"}:
        click.echo(click.style('Parser does not exist.', fg='red'))
        return


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
            click.echo(click.style('WIP FEATURE!', fg='red'))
    
    if commands != []:
        # Parse and execute every command using correct parser
        color("black", "blue")
        begin_fill()
        for command in commands:
            execute_command(command, parser)
        end_fill()
        done()

if __name__ == "__main__":
    speed(1)
    #tracer(10, 0)
    screensize(800, 600)
    etchy_cli()