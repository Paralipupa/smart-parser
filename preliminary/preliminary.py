import sys
import os
import argparse
from pp_service import pp_service
from pp_charges import pp_charges
from pp import pp
from accounts import accounts
from columns import set_columns
from header import header
from pu import pu
from puv import puv

def getArgs() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', nargs='?')
    return parser


def read(file_name: str) -> list:
    lines = {'0': [], '1': [], '2': []}
    with open(file_name, 'r') as file:
        for line in file:
            if line[0] != ';':
                if line[:2] == '0:':
                    lines['0'].extend(
                        [{'name': x, 'is_unique': True, 'is_optional': False if len(lines['0']) == 0 else True} for x in line[2:].split('\t')])
                elif line[:2] == '1:':
                    lines['1'].extend(
                        [{'name': x.strip(), 'is_unique': False, 'is_optional': True} for x in line[2:].split('\t')
                         if x.strip() != '' and not any(y for y in lines['1'] if y['name'].strip() == x.strip())])
                elif line[:2] == '2:':
                    lines['2'].extend(
                        [{'name': x, 'is_unique': False, 'is_optional': True} for x in line[2:].split('\t')
                         if x.strip() != '' and not any(y for y in lines['2'] if y['name'].strip() == x.strip())])
    lines['1'] = sorted(lines["1"], key=lambda x: x['name'])
    lines['1'].append({'name': 'Прочие'})
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
    pu(lines, os.path.dirname(namespace.name))
    puv(lines, os.path.dirname(namespace.name))
