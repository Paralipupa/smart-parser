import re
from utils import get_ident, get_reg
from settings import *


def set_columns(lines: list, path: str):

    with open(f'{path}/ini/1_col.ini', 'w') as file:
        file.write(';########################################################################################################################\n')
        file.write(';-------------------------------------------------------------- колонки -------------------------------------------------\n')
        file.write(';########################################################################################################################\n')
        for i, line in enumerate(lines["0"]):
            file.write(f'[col_{i}]\n')
            if i == 0:
                file.write(f'name=ЛС\n')
                file.write(f'condition_begin_team=@ЛС\n')
                file.write('col_data_offset=+0\n')
            else:
                file.write(f'name={get_ident(line["name"].split(";")[0])}\n')
            for j, x in enumerate(get_reg(line["name"]).split(';')):
                file.write(
                    f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={x}\n')
            if line["is_optional"]:
                file.write(f'is_optional=true\n')
            file.write('is_unique=true\n\n')

        for i, line in enumerate(lines["1"][:-1]):
            file.write(f'[col_{COLUMN_BEGIN+i}]\n')
            x = get_ident(line["name"].split(";")[0])
            file.write(f'name={x}\n')
            for j, x in enumerate(get_reg(line["name"]).split(';')):
                file.write(
                    f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={x}\n')
            file.write('border_column_left=2\n')
            file.write('border_column_right=4\n')
            file.write('is_optional=true\n\n')
        line = lines["1"][i+1]
        file.write(f'[col_{COLUMN_BEGIN+1+i}]\n')
        file.write(f'name={get_ident(line["name"])}\n')
        file.write(f'pattern=.+\n')
        file.write('border_column_left=2\n')
        file.write('border_column_right=4\n')
        file.write('is_only_after_stable=true\n\n')

        for i, line in enumerate(lines["2"]):
            file.write(f'[col_{COLUMN_BEGIN+i+len(lines["1"])}]\n')
            x = get_ident(line["name"].split(";")[0])
            file.write(f'name={x}\n')
            for j, x in enumerate(get_reg(line["name"]).split(';')):
                file.write(
                    f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={x}\n')
            file.write('is_optional=true\n\n')
