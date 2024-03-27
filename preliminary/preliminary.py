import sys
import os

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path)

import argparse
import configparser
from pp_service import pp_service
from pp_charges import pp_charges
from pp import pp
from accounts import accounts
from columns import set_columns
from header import header
from pu import pu
from puv import puv
from utils import write_config, sorted_lines, set_lines, set_parameters, get_ident
from module.helpers import getArgs

def read_from_config(file_name: str) -> list:
    lines = set_lines()
    config: configparser.ConfigParser = configparser.ConfigParser()
    config.read(file_name, encoding="utf-8")
    i = 20
    while config.has_section(f'col_{i}'):
        if config[f'col_{i}'].get('pattern', ''):
            is_optional = config[f'col_{i}'].get('is_optional', 'False')
            pattern = config[f'col_{i}'].get('pattern', 'False')
            lines['1'].extend([{'name': get_ident(pattern).strip(), 'is_unique': False,
                              'is_optional': True if is_optional else False,
                              'pattern': pattern
                                }])
        i += 1
    return lines


def read_from_text(file_name: str) -> list:
    # 0 Данные пользователя и ОСВ (accounts, pp)
    # 1 Начисление платежей  (pp_charges)
    #   1a Наимменование услуг при иерархической структуре
    # 2 Показания приборов учета (pu, puv)
    #   2a Наимменование услуг при иерархической структуре
    # 3 Мусор
    # 9 Все вместе
    parameters = set_parameters()
    lines = set_lines()
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
                elif line[:8] == "filename":
                    lines["filename"] = line[9:].strip()
                elif line[:8] == 'pattern_':
                    k = line.find(':')
                    if k > 8:
                        p = line[:k]
                        lines['param'].setdefault(p, [])
                        lines['param'][p].append(line[len(p)+1:].strip())
                elif line[:9] == 'required_':
                    k = line.find(':')
                    if k > 9:
                        p = line[:k]
                        lines['required'].setdefault(p, [])
                        lines['required'][p].append(line[len(p)+1:].strip())
                elif line[:7] == 'header_':
                    k = line.find(':')
                    if k > 7:
                        p = line[:k]
                        lines['param'].setdefault(p, [])
                        lines['param'][p].append(line[len(p)+1:].strip())
                elif line.find(':') != -1:
                    k = line.find(':')
                    p = line[:k]
                    lines['param'].setdefault(p, [])
                    lines['param'][p].append(line[len(p)+1:].strip())
                else:
                    for p in parameters:
                        if line[:len(p)] == p:
                            lines['param'].setdefault(p, [])
                            lines['param'][p].append(line[len(p)+1:].strip())
    lines = sorted_lines(lines)
    if len(lines['1a']) == 0 and len(lines['2a']) == 0:
        lines['1'].append({'name': 'Прочие', 'is_unique': False, 'is_optional': True})
    else:
        lines['1a'].append({'name': 'Прочие', 'is_unique': False, 'is_optional': True})
    return lines


if __name__ == "__main__":
    names = []
    args = getArgs()
    namespace = args.parse_args(sys.argv[1:])
    lines = read_from_text(namespace.name)
    cols = set_columns(lines, os.path.dirname(__file__))
    names.append(header(lines, os.path.dirname(__file__)))
    names.append(cols)
    names.append(accounts(lines, os.path.dirname(__file__)))
    names.append(pp(lines, os.path.dirname(__file__)))
    names.append(pp_charges(lines, os.path.dirname(__file__)))
    names.append(pp_service(lines, os.path.dirname(__file__)))
    names.append(pu(lines, os.path.dirname(__file__)))
    names.append(puv(lines, os.path.dirname(__file__)))
    write_config(
        names, os.path.join(os.path.dirname(__file__), "ini"), "gis_config.ini"
    )
    if lines.get("filename"):
        write_config(
            names,
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "config"),
            lines.get("filename"),
        )
