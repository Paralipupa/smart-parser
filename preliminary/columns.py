import re
from settings import *

def get_ident(name: str) -> str:
    # name = [item.capitalize() for item in name]
    result = "".join(c for c in name.title() if c.isalnum())
    result = result.replace('Итого','')
    return result

def get_reg(name: str) -> str:
    name = name.replace('\\','\\\\').replace('.','\.')
    name = name.replace('(','\(').replace(')','\)')
    name = name.replace('[','\[').replace(']','\]')
    return f'^{name.rstrip()}$'


def set_columns(lines: list, path: str):

    with open(f'{path}/ini/1_col.ini', 'w') as file:
        file.write(';---- колонки ------------\n')
        for i, line in enumerate(lines["0"]):
            file.write(f'[col_{i}]\n')
            if i == 0:
                file.write(f'name=ЛС\n')
                file.write(f'condition_begin_team=@ЛС\n')
            else:
                file.write(f'name={get_ident(line["name"])}\n')
            file.write(f'pattern={get_reg(line["name"])}\n')
            if line["is_optional"]:
                file.write(f'is_optional=true\n')
            file.write('is_unique=true\n\n')

        for i, line in enumerate(lines["1"][:-1]):
            file.write(f'[col_{COLUMN_BEGIN+i}]\n')
            file.write(f'name={get_ident(line["name"])}\n')
            file.write(f'pattern={get_reg(line["name"])}\n')
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
