import click

@click.command()
@click.option("--inputfile", help="Input file to read the number from.")
@click.option('--outputfile', help='File to use as an output.')
@click.option('--multfactor', help='Factor by which to multiply the digits to get an angle')
def write_num_instr(inputfile, outputfile, multfactor):
    digits = None
    with open(inputfile) as pifile:
        digits = pifile.read()
        digits = digits[2:]

    with open(outputfile, "w") as pi_instr:
        for i, digit in enumerate(digits):
            if i % 2 == 0:
                pi_instr.write(f"ROTATE_LD {float(digit)*float(multfactor)}\n")
            else:
                pi_instr.write(f"ROTATE_RD {float(digit)*float(multfactor)}\n")
            pi_instr.write(f"FORWARD 10\n")

if __name__ == "__main__":
    write_num_instr()