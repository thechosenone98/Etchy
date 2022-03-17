from email.policy import default
from turtle import *
import csv
import click
import os


def parse_csv_command(command):
    pass

def parse_tcode_command(command):
    pass

def execute_command(command, parser):
    if parser == "CSV":
        command, argument = parse_csv_command()
    elif parser == "TCODE":
        command, argument = parse_tcode_command()


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

    if parser == "CSV":
        with open(inputfile, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                for command in row:
                    commands.append(command)

        color('red', 'yellow')
        begin_fill()
        for command in commands:
            if command[0] == "L":
                forward(int(command[1:]))
            elif command[0] == "A":
                left(int(command[1:]))
            else:
                continue
        end_fill()
        done()
    else:
        click.echo(click.style('NOT IMPLEMENTED! WIP FEATURE!', fg='red'))

if __name__ == "__main__":
    etchy_cli()