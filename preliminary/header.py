import re
from utils import get_ident, get_reg, get_name
from settings import *


def header(lines: list, path: str) -> str:
    patts = []
    names = []
    file_name = f'{path}/ini/0_header.ini'
    with open(file_name, 'w') as file:
        file.write(
            f';--------------- {lines["param"].get("name",[""])[0] } ----------------\n')
        file.write('[check]\n')
        file.write(
            '; Поиск ключевого значения по строке(ам) для определения совместимости\n')
        file.write('; входных данных и конфигурации\n')
        file.write('row=0<15\n')
        if lines["param"].get("pattern_check"):
            for i, p in enumerate(lines["param"]["pattern_check"]) :
                file.write(f'pattern{"_" if i>0 else ""}{i-1 if i>0 else ""}={p}\n')
        file.write('\n')

        file.write('[main]\n')
        file.write('path_output=output\n')
        file.write('row_start=0\n')
        file.write('page_name=\n')
        file.write('page_index=0\n')
        file.write('max_columns=150\n')
        file.write('max_rows_heading=20\n')
        if lines['param'].get('border_column_left'):
            file.write(f'border_column_left={lines["param"]["border_column_left"][0]}\n')
        if lines['param'].get('border_column_right'):
            file.write(f'border_column_right={lines["param"]["border_column_right"][0]}\n')
        file.write('\n')

        file.write(';---- шаблоны регулярных выражений ------------\n\n')
        file.write('[pattern]\n')
        file.write('name=currency\n')
        file.write('pattern=^-?\d{1,7}(?:[\.,]\d{1,3})?$\n')
        file.write('\n')

        k = 0
        for key, val in lines['param'].items():
            if key[:8] == 'pattern_':
                file.write(f'[pattern_{k}]\n')
                file.write(f'name={key[8:]}\n')
                for i, p in enumerate(val) :
                    file.write(f'pattern{"_" if i>0 else ""}{i-1 if i>0 else ""}={p}\n')
                file.write('\n')
                k += 1

        for i, line in enumerate(lines["1a"]):
            file.write(f'[pattern_{COLUMN_BEGIN+i}]\n')
            name = get_name(get_ident(line["name"].split(";")[0]), names)
            file.write(f'name={name}\n')
            for j, x in enumerate(get_reg(line["name"]).split(';')):
                file.write(
                    f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={x}\n')
            file.write(f'\n')
        if (len(lines["1a"]) > 1 and lines["1a"][-1]['name'] == 'Прочие'):
            file.write(f'pattern_0=.+\n')
        file.write('\n')

        file.write(
            ';--------------------------------------------------- параметры --------------------------------------------------\n\n')
        k = 0
        for key, val in lines['param'].items():
            if key[:8] == 'pattern_':
                file.write(f'[headers_{k}]\n')
                file.write(f'name={key[8:]}\n')
                file.write(f'pattern=@{key[8:]}\n')
                file.write('\n')
                k += 1

        file.write(f'[headers_{k}]\n')
        file.write('name=timezone\n')
        file.write('pattern=@+3\n\n')
        k += 1

    return file_name
