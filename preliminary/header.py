import re
from utils import get_ident, get_reg, get_name
from settings import *

def header(lines:list, path: str):
    patts = []
    names = []
    with open(f'{path}/ini/0_header.ini', 'w') as file:
        file.write(';---------------ТСЖ "Шустовъ парк"----------------\n')
        file.write('[check]\n')
        file.write('; Поиск ключевого значения по строке(ам) для определения совместимости\n')
        file.write('; входных данных и конфигурации\n')
        file.write('row=0<15\n')
        file.write('pattern=Шустовъ парк\n')

        file.write('[main]\n')
        file.write('path_output=output\n')
        file.write('row_start=0\n')
        file.write('page_name=\n')
        file.write('page_index=0\n')
        file.write('max_columns=150\n')
        file.write('max_rows_heading=20\n\n')

        file.write(';---- шаблоны регулярных выражений ------------\n\n')

        file.write('[pattern]\n')
        file.write('name=period\n')
        file.write('pattern=(?<=Начало периода: )[0-9]{2}\.{0-9}{2}\.[0-9]{4}\n\n')

        file.write('[pattern_0]\n')
        file.write('name=currency\n')
        file.write('pattern=^-?\d{1,7}(?:[\.,]\d{1,3})?$\n\n')

        file.write('[pattern_1]\n')
        file.write('name=ЛС\n')
        file.write('pattern=^[0-9]{1,6}-[0-9]+(?=,)\n')
        file.write('pattern_0=^[0-9]{1,6}(?=,)\n')
        file.write('pattern_1=^[0-9]{1,6}-П(?=,)\n')
        file.write('pattern_2=^[0-9-]{8}$|^[0-9-]{2,3}$\n\n')

        for i, line in enumerate(lines["1a"]):
            file.write(f'[pattern_{COLUMN_BEGIN+i}]\n')
            name = get_name(get_ident(line["name"].split(";")[0]), names)
            file.write(f'name={name}\n')
            for j, x in enumerate(get_reg(line["name"]).split(';')):
                file.write(
                    f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={x}\n')
            file.write(f'\n')
        file.write(f'pattern_0=.+\n')

        file.write(';--------------------------------------------------- параметры --------------------------------------------------\n\n')

        file.write('[headers_0]\n')
        file.write('name=period\n')
        file.write('row=0<5\n')
        file.write('column=0<5\n')
        file.write('pattern=@period\n\n')

        file.write('[headers_1]\n')
        file.write('name=inn\n')
        file.write('pattern=@4727000113\n\n')

        file.write('[headers_2]\n')
        file.write('name=timezone\n')
        file.write('pattern=@+3\n\n')
