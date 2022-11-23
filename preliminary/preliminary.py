import sys, os
import argparse
from pp_service import pp_service
from pp_charges import pp_charges
# from pp import pp
from columns import set_columns


def getArgs() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', nargs='?')
    parser.add_argument('-i', '--inn', nargs='?')
    parser.add_argument('-c', '--config', nargs='?')
    parser.add_argument('-u', '--union', nargs='?')
    return parser

def read(file_name: str) -> list:
    lines = []
    with open(file_name, 'r') as file:
        for line in file:
            lines.extend(line.split('\t'))
    lines.append('Прочие')
    return lines

if __name__ == "__main__":
    args = getArgs()
    namespace = args.parse_args(sys.argv[1:])
    lines = read(namespace.name)
    # pp(lines, os.path.dirname(namespace.name))
    pp_charges(lines, os.path.dirname(namespace.name))
    pp_service(lines, os.path.dirname(namespace.name))
    set_columns(lines, os.path.dirname(namespace.name))
