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
from utils import write_config, sorted_lines


def getArgs() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', nargs='?')
    return parser


def read(file_name: str) -> list:
    # 0 Данные пользователя и ОСВ (accounts, pp)
    # 1 Начисление платежей  (pp_charges)
    #   1a Наимменование услуг при иерархической структуре
    # 2 Показания приборов учета (pu, puv)
    #   2a Наимменование услуг при иерархической структуре
    # 3 Мусор
    # 9 Все вместе
    parameters = ['name', 'check', 'inn', 'fias', 'period', 'ЛС', 
                  'border_column_left', 'border_column_right']
    lines = {'0': [], '1': [], '1a': [], '2': [],
             '2a': [], '3': [], '9': [], 'param': {}, 'dic': {}}
    with open(file_name, 'r') as file:
        for line in file:
            if line[0] != ';':
                if line[:2] == '0:':
                    l = [{'name': x, 'is_unique': True, 'is_optional': False if len(
                        lines['0']) == 0 else True} for x in line[2:].split('\t')
                        if x.strip() != '' and not any(y for y in lines['9'] if y['name'].strip() == x.strip())]
                    lines['0'].extend(l)
                    lines['9'].extend(l)
                elif line[:2] == '1:':
                    l = [{'name': x.strip(), 'is_unique': False, 'is_optional': True} for x in line[2:].split('\t')
                         if x.strip() != '' and not any(y for y in lines['9'] if y['name'].strip() == x.strip())]
                    lines['1'].extend(l)
                    lines['9'].extend(l)
                elif line[:2] == '2:':
                    l = [{'name': x.strip(), 'is_unique': False, 'is_optional': True} for x in line[2:].split('\t')
                         if x.strip() != '' and not any(y for y in lines['9'] if y['name'].strip() == x.strip())]
                    lines['2'].extend(l)
                    lines['9'].extend(l)
                elif line[:2] == '3:':
                    l = [{'name': x.strip(), 'is_unique': False, 'is_optional': True} for x in line[2:].split('\t')
                         if x.strip() != '' and not any(y for y in lines['9'] if y['name'].strip() == x.strip())]
                    lines['3'].extend(l)
                    lines['9'].extend(l)
                elif line[:3] == '1a:':
                    l = [{'name': x.strip(), 'is_unique': False, 'is_optional': True} for x in line[3:].split('\t')
                         if x.strip() != '' and not any(y for y in lines['9'] if y['name'].strip() == x.strip())]
                    lines['1a'].extend(l)
                    lines['9'].extend(l)
                elif line[:3] == '2a:':
                    l = [{'name': x.strip(), 'is_unique': False, 'is_optional': True} for x in line[3:].split('\t')
                         if x.strip() != '' and not any(y for y in lines['9'] if y['name'].strip() == x.strip())]
                    lines['2a'].extend(l)
                    lines['9'].extend(l)
                else:
                    for p in parameters:
                        if line[:len(p)] == p:
                            lines['param'].setdefault(p,[])
                            lines['param'][p].append(line[len(p)+1:].strip()) 
    lines = sorted_lines(lines)
    if len(lines['1a']) == 0 and len(lines['2a']) == 0:
        lines['1'].append({'name': 'Прочие'})
    else:
        lines['1a'].append({'name': 'Прочие'})
    return lines


if __name__ == "__main__":
    names = []
    args = getArgs()
    namespace = args.parse_args(sys.argv[1:])
    lines = read(namespace.name)
    names.append(header(lines, os.path.dirname(__file__)))
    names.append(set_columns(lines, os.path.dirname(__file__)))
    names.append(accounts(lines, os.path.dirname(__file__)))
    names.append(pp(lines, os.path.dirname(__file__)))
    names.append(pp_charges(lines, os.path.dirname(__file__)))
    names.append(pp_service(lines, os.path.dirname(__file__)))
    names.append(pu(lines, os.path.dirname(__file__)))
    names.append(puv(lines, os.path.dirname(__file__)))
    write_config(names, os.path.dirname(__file__))
