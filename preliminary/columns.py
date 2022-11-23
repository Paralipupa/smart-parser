import re

def get_ident(name: str) -> str:
    return "".join(c for c in name if c.isalnum())

def get_reg(name: str) -> str:
    name = name.replace('\\','\\\\').replace('.','\.')
    name = name.replace('(','\(').replace(')','\)')
    name = name.replace('[','\[').replace(']','\]')
    return f'^{name.rstrip()}$'


def set_columns(lines: list, path: str):

    with open(f'{path}/col.ini', 'w') as file:
        file.write(';---- колонки ------------\n')
        file.write('[col_0]\n')
        file.write('name=ЛС\n')
        file.write('pattern=^Лицевой счет$\n')
        file.write('condition_begin_team=@ЛС\n')
        file.write('is_unique=true\n\n')

        file.write('[col_1]\n')
        file.write('name=Сальдо на начало\n')
        file.write('pattern=^Итого Задолженность на начало$\n')
        file.write('is_unique=true\n\n')

        file.write('[col_2]\n')
        file.write('name=Начислено\n')
        file.write('pattern=^Итого Начислено$\n')
        file.write('is_unique=true\n\n')

        file.write('[col_3]\n')
        file.write('name=Оплачено\n')
        file.write('pattern=^Итого Оплачено$\n')
        file.write('is_unique=true\n\n')

        file.write('[col_4]\n')
        file.write('name=Сальдо на конец\n')
        file.write('pattern=^Итого Задолженность на конец$\n')
        file.write('is_unique=true\n\n')

        file.write('[col_5]\n')
        file.write('name=Пени\n')
        file.write('pattern=^Пени$\n')
        file.write('border_column_left=2\n')
        file.write('border_column_right=4\n')
        file.write('is_unique=true\n')
        file.write('is_optional=true\n\n')

        file.write('[col_6]\n')
        file.write('name=Адрес\n\n')

        file.write('[col_7]\n')
        file.write('name=Квартира\n\n')

        file.write('[col_8]\n\n')
        file.write('name=Площадь\n\n')

        file.write('[col_9]\n')
        file.write('name=Проживающие\n\n')

        for i, line in enumerate(lines[:-1]):
            file.write(f'[col_{10+i}]\n')
            file.write(f'name={get_ident(line)}\n')
            file.write(f'pattern={get_reg(line)}\n')
            file.write('border_column_left=2\n')
            file.write('border_column_right=4\n')
            file.write('is_optional=true\n\n')
        line = lines[i+1]
        file.write(f'[col_{11+i}]\n')
        file.write(f'name={get_ident(line)}\n')
        file.write(f'pattern=.+\n')
        file.write('border_column_left=2\n')
        file.write('border_column_right=4\n')
        file.write('is_only_after_stable=true\n\n')
