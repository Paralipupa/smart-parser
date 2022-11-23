import sys, os
import argparse
from pp_service import pp_service
from pp_charges import pp_charges
from pp import pp
from accounts import accounts
from columns import set_columns
from header import header


def getArgs() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', nargs='?')
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
    header(lines, os.path.dirname(namespace.name))
    set_columns(lines, os.path.dirname(namespace.name))
    accounts(lines, os.path.dirname(namespace.name))
    pp(lines, os.path.dirname(namespace.name))
    pp_charges(lines, os.path.dirname(namespace.name))
    pp_service(lines, os.path.dirname(namespace.name))
