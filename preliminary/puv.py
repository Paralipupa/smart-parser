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
            if lines["dic"].get("service"):
                file.write(f'offset_col_config={lines["dic"]["service"][0]["col"]}\n')
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f'offset_pattern=@{name}\n')
            else:
                file.write(f'offset_col_config=0\n')
                file.write(f'offset_pattern=.+\n')
            if lines["dic"].get("internal_id_pu"):
                file.write(f'func=id+{get_ident(lines["dic"]["internal_id_pu"][0]["name"])}+ПУП,spacerepl,hash\n')
            else:
                file.write(
                    f'func=id+{l[0]["name"].split(";")[0].replace(","," ").replace("+","")}+ПУП,spacerepl,hash\n')
            if lines["dic"].get("internal_id_pu"):
                for i, line in enumerate(lines["dic"]["internal_id_pu"][1:]):
                    file.write(f'[puv_1_{i}]\n')
                    file.write('; Внутренний идентификатор ПУП\n')
                    file.write(f'func=id+{get_ident(line["name"])}+ПУП,spacerepl,hash\n')
            else:
                for i, line in enumerate(l[1:]):
                    file.write(f'[puv_1_{i}]\n')
                    if lines["dic"].get("service"):
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
            if lines["dic"].get("service"):
                file.write(f'offset_col_config={lines["dic"]["service"][0]["col"]}\n')
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f'offset_pattern=@{name}\n')
            else:
                file.write(f'offset_col_config=0\n')
                file.write(f'offset_pattern=.+\n')
            if lines["dic"].get("internal_id_pu"):
                file.write(f'func=id+{get_ident(lines["dic"]["internal_id_pu"][0]["name"])}+ПУ,spacerepl,hash\n')
            else:
                file.write(
                    f'func=id+{l[0]["name"].split(";")[0].replace(","," ").replace("+","")}+ПУ,spacerepl,hash\n\n')
            if lines["dic"].get("internal_id_pu"):
                for i, line in enumerate(lines["dic"]["internal_id_pu"][1:]):
                    file.write(f'[puv_3_{i}]\n')
                    file.write('; Внутренний идентификатор ПУ\n')
                    file.write(f'func=id+{get_ident(line["name"])}+ПУ,spacerepl,hash\n')
            else:
                for i, line in enumerate(l[1:]):
                    file.write(f'[puv_3_{i}]\n')
                    if lines["dic"].get("service"):
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
            if lines["dic"].get("service"):
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f'pattern=@{name}\n')
                file.write(f'col_config={lines["dic"]["service"][0]["col"]}\n')
                file.write(f'offset_col_config={lines["dic"]["rr1"][0]["col"]}\n')
                file.write('offset_pattern=.+\n')
                file.write('offset_type=float\n')
                file.write('func=round6\n')
                for i, line in enumerate(l[1:]):
                    file.write(f'[puv_5_{i}]\n')
                    file.write('; Показание 1\n')
                    file.write(f'; {line["name"].rstrip()}\n')
                    name = get_name(get_ident(line["name"].split(";")[0]), names)
                    file.write(f'pattern=@{name}\n')
            else:
                file.write("pattern=@0\n")
                file.write("col_config=0\n")
                file.write(
                    f'offset_col_config={lines["dic"]["rr1"][0]["col"]}\n'
                )
                file.write("offset_pattern=.+\n")
                file.write('offset_type=float\n')
                file.write('func=round6\n')
                for i, line in enumerate(lines["dic"]["rr1"][1:]):
                    file.write(f'[puv_5_{i}]\n')
                    file.write('; Показание 1\n')
                    file.write(
                        f'offset_col_config={line["col"]}\n'
                    )
        file.write('\n')

        file.write('[puv_6]\n')
        file.write('; Показание 2\n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=rr2\n')
        if lines["dic"].get("rr2"):
            if lines["dic"].get("service"):
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f'pattern=@{name}\n')
                file.write(f'col_config={lines["dic"]["service"][0]["col"]}\n')
                file.write(f'offset_col_config={lines["dic"]["rr2"][0]["col"]}\n')
                file.write('offset_pattern=.+\n')
                file.write('offset_type=float\n')
                file.write('func=round6\n')
                for i, line in enumerate(l[1:]):
                    file.write(f'[puv_6_{i}]\n')
                    file.write('; Показание 2\n')
                    file.write(f'; {line["name"].rstrip()}\n')
                    name = get_name(get_ident(line["name"].split(";")[0]), names)
                    file.write(f'pattern=@{name}\n')
            else:
                file.write("pattern=@0\n")
                file.write("col_config=0\n")
                file.write(
                    f'offset_col_config={lines["dic"]["rr2"][0]["col"]}\n'
                )
                file.write("offset_pattern=.+\n")
                file.write('offset_type=float\n')
                file.write('func=round6\n')
                for i, line in enumerate(lines["dic"]["rr2"][1:]):
                    file.write(f'[puv_6_{i}]\n')
                    file.write('; Показание 2\n')
                    file.write(
                        f'offset_col_config={line["col"]}\n'
                    )
        file.write('\n')

        file.write('[puv_7]\n')
        file.write('; Показание 3\n')
        file.write(f'; {l[0]["name"]}\n')
        file.write('name=rr3\n')
        if lines["dic"].get("rr3"):
            if lines["dic"].get("service"):
                name = get_name(get_ident(l[0]["name"].split(";")[0]), names)
                file.write(f'pattern=@{name}\n')
                file.write(f'col_config={lines["dic"]["service"][0]["col"]}\n')
                file.write(f'offset_col_config={lines["dic"]["rr3"][0]["col"]}\n')
                file.write('offset_pattern=.+\n')
                file.write('offset_type=float\n')
                file.write('func=round6\n')
                for i, line in enumerate(l[1:]):
                    file.write(f'[puv_7_{i}]\n')
                    file.write('; Показание 3\n')
                    file.write(f'; {line["name"].rstrip()}\n')
                    name = get_name(get_ident(line["name"].split(";")[0]), names)
                    file.write(f'pattern=@{name}\n')
            else:
                file.write("pattern=@0\n")
                file.write("col_config=0\n")
                file.write(
                    f'offset_col_config={lines["dic"]["rr3"][0]["col"]}\n'
                )
                file.write("offset_pattern=.+\n")
                file.write('offset_type=float\n')
                file.write('func=round6\n')
                for i, line in enumerate(lines["dic"]["rr3"][1:]):
                    file.write(f'[puv_7_{i}]\n')
                    file.write('; Показание 3\n')
                    file.write(
                        f'offset_col_config={line["col"]}\n'
                    )
        file.write('\n')
    return file_name
