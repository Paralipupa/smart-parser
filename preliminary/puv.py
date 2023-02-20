from utils import get_ident, get_name, get_lines
from settings import *


def puv(lines: list, path: str) -> str:
    names = []
    l = get_lines(lines)
    file_name = f'{path}/ini/7_puv.ini'
    with open(file_name, 'w') as file:
        file.write(
            ';########################################################################################################################\n')
        file.write(
            ';-------------------------------------------------------------- puv -----------------------------------------------------\n')
        file.write(
            ';########################################################################################################################\n')
        file.write('[doc_5]\n')
        file.write('; ПУ показания\n')
        file.write('name=puv\n')
        file.write('required_fields=rr1\n\n')

        file.write('[puv_0]\n')
        file.write('; ИНН, ОГРН или OrgID\n')
        file.write('name=org_ppa_guid\n')
        file.write('pattern=@\n')
        file.write('col_config=0\n')
        file.write('row_data=0\n')
        file.write('func=inn\n\n')

        file.write('[puv_1]\n')
        file.write('; Внутренний идентификатор ПУП\n')
        file.write('name=internal_id\n')
        if lines["dic"].get("rr1"):
            file.write('pattern=@0\n')
            file.write('col_config=0\n')
            file.write('row_data=0\n')
            if not (len(lines['1a']) == 0 and len(lines['2a']) == 0):
                file.write(f'offset_col_config={lines["dic"].get("service", {"col":20})["col"]}\n')
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f'offset_pattern=@{name}\n')
            else:
                file.write(f'offset_col_config=0\n')
                file.write(f'offset_pattern=.+\n')
            file.write(
                f'func=id+{l[0]["name"].split(";")[0].replace(","," ").replace("+","")}+ПУП,spacerepl,hash\n\n')
            for i, line in enumerate(l[1:]):
                file.write(f'[puv_1_{i}]\n')
                if not (len(lines['1a']) == 0 and len(lines['2a']) == 0):
                    name = get_name(get_ident(line["name"].split(";")[0]), names)
                    file.write(f'offset_pattern=@{name}\n')
                file.write(
                    f'func=id+{line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()}+ПУП,spacerepl,hash\n')
        file.write('\n')

        file.write('[puv_2]\n')
        file.write('; ГИС. Идентификатор ПУП GUID\n')
        file.write('name=gis_id\n\n')

        names = []
        file.write('[puv_3]\n')
        file.write('; Внутренний идентификатор ПУ\n')
        file.write('name=metering_device_internal_id\n')
        if lines["dic"].get("rr1"):
            file.write('pattern=@0\n')
            file.write('col_config=0\n')
            file.write('row_data=0\n')
            if not (len(lines['1a']) == 0 and len(lines['2a']) == 0):
                file.write(f'offset_col_config={lines["dic"].get("service", {"col":20})["col"]}\n')
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f'offset_pattern=@{name}\n')
            else:
                file.write(f'offset_col_config=0\n')
                file.write(f'offset_pattern=.+\n')
            file.write(
                f'func=id+{l[0]["name"].split(";")[0].replace(","," ").replace("+","")}+ПУ,spacerepl,hash\n\n')
            for i, line in enumerate(l[1:]):
                file.write(f'[puv_3_{i}]\n')
                if not (len(lines['1a']) == 0 and len(lines['2a']) == 0):
                    name = get_name(get_ident(line["name"].split(";")[0]), names)
                    file.write(f'offset_pattern=@{name}\n')
                file.write(
                    f'func=id+{line["name"].split(";")[0].replace(","," ").replace("+","").rstrip()}+ПУ,spacerepl,hash\n')
        file.write('\n')

        file.write('[puv_4]\n')
        file.write('; Дата\n')
        file.write('name=date\n')
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        file.write('row_data=\n')
        file.write('func=period_last\n\n')

        names = []
        file.write('[puv_5]\n')
        file.write('; Показание 1\n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=rr1\n')
        if lines["dic"].get("rr1"):
            if not (len(lines['1a']) == 0 and len(lines['2a']) == 0):
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f'pattern=@{name}\n')
                file.write(f'col_config={lines["dic"].get("service", {"col":20})["col"]}\n')
                file.write(f'offset_col_config={lines["dic"].get("rr1", {"col":""})["col"]}\n')
                file.write('offset_pattern=.+\n')
                file.write('offset_type=float\n')
                file.write('func=round6\n\n')
            else:
                file.write('pattern=@0\n')
                file.write('col_config=0\n')
                file.write('row_data=0\n')
                file.write(f'offset_col_config={COLUMN_BEGIN}\n')
                file.write('offset_pattern=.+\n')
                file.write('offset_type=float\n')
                file.write('func=round6\n\n')
            for i, line in enumerate(l[1:]):
                if not (len(lines['1a']) == 0 and len(lines['2a']) == 0):
                    file.write(f'[puv_5_{i}]\n')
                    file.write('; Показание 1\n')
                    file.write(f'; {line["name"].rstrip()}\n')
                    name = get_name(get_ident(line["name"].split(";")[0]), names)
                    file.write(f'pattern=@{name}\n\n')
                else:
                    file.write(f'[puv_5_{i}]\n')
                    file.write('; Показание 1\n')
                    file.write(f'; {line["name"].rstrip()}\n')
                    file.write(f'offset_col_config={COLUMN_BEGIN+1+i}\n')
        file.write('\n')

        file.write('[puv_6]\n')
        file.write('; Показание 2\n')
        file.write('name=rr2\n\n')

        file.write('[puv_7]\n')
        file.write('; Показание 3\n')
        file.write('name=rr3\n\n')
    return file_name
