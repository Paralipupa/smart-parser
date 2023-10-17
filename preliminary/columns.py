import re
from utils import get_ident, get_reg, get_name, get_pattern, \
    get_param_offset, get_param_function, get_param_type, get_param_anchor,\
    get_param_function_is_no_return
    
from settings import *


def set_columns(lines: list, path: str) -> str:
    file_name = f"{path}/ini/1_col.ini"
    with open(file_name, "w") as file:
        patts = []
        names = []
        file.write(
            ";########################################################################################################################\n"
        )
        file.write(
            ";-------------------------------------------------------------- колонки -------------------------------------------------\n"
        )
        file.write(
            ";########################################################################################################################\n"
        )
        parsing_lines(file, lines["0"], lines["dic"],
                      lines["param"], names, patts, 0)
        parsing_lines(file, lines["2"], lines["dic"], lines["param"],
                      names, patts, len(lines["0"]))
        parsing_lines(file, lines["3"], lines["dic"], lines["param"],
                      names, patts, len(lines["0"])+len(lines["2"]))
        parsing_lines(file, lines["1"], lines["dic"], lines["param"],
                      names, patts, COLUMN_BEGIN)
        if not lines["dic"].get("service"):
            file.write("is_only_after_stable=true\n")
            file.write(f"pattern_0=.+\n")
        file.write("\n")

    return file_name


def parsing_lines(file, lines: list, ldict: dict, lparam: dict, names: list, patts: list, col_begin: int):
    for idx_col, line in enumerate(lines):
        file.write("\n")
        file.write(f"[col_{col_begin + idx_col}]\n")
        line["name"], anchor = get_param_anchor(line["name"])
        if line["name"][0] == ">":
            # проверяем левую границу Услуг
            lparam["main_border_column_left"] = [idx_col]
            line["name"] = line["name"][1:]
        if line["name"][0] == "<":
            # проверяем правую границу Услуг
            lparam["main_border_column_right"] = [idx_col]
            line["name"] = line["name"][1:]
        ls = line["name"].split("@")
        line["name"] = ls[0]
        for x in ls[1:]:
            x, param_off = get_param_offset(x)
            x, param_func = get_param_function(x)
            x, param_func_is_no = get_param_function_is_no_return(x)
            x, param_type = get_param_type(x)
            x, param_pattern = get_pattern(x)
            ldict.setdefault(x, [])
            ldict[x].append(
                {"name": ls[0], "col": col_begin + idx_col,
                 "pattern": param_pattern,
                 "offset": param_off,
                 "func": param_func,
                 "func_is_no": param_func_is_no,
                 "type": param_type}
            )
        if col_begin + idx_col == 0:
            file.write(f"name=ЛС\n")
            file.write(f"condition_begin_team=@ЛС\n")
        else:
            name = get_name(get_ident(line["name"].split(";")[0]), names)
            file.write(f"name={name}\n")
        is_duplicate = False
        col_offset = ''
        for j, x in enumerate(get_reg(line["name"]).split(";")):
            col_off: str = re.sub(r"\(|\)|\+|-|\^|\$|\\|,|\s", "", x)
            if str(col_off).isdigit():
                col_off: str = re.sub(r"\^|\$|\\", "", x)
                col_offset += col_off + ","
            else:
                file.write(
                    f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={x}\n'
                )
                if not any([y for y in patts if y == x]):
                    patts.append(x)
                else:
                    is_duplicate = True
        if not ldict.get("service"):
            if idx_col == len(lines)-1 and  col_begin > 0 and lparam.get("main_border_column_left"):
                file.write(
                    f'border_column_left={lparam.get("main_border_column_left", ["2"])[0]}\n'
                )
            if idx_col == len(lines)-1 and col_begin > 0 and lparam.get("main_border_column_right"):
                file.write(
                    f'border_column_right={lparam.get("main_border_column_right", ["4"])[0]}\n'
                )
        if col_offset:
            file.write(
                f'col_data_offset=+0,{col_offset.strip(",")}\n'
            )
        if anchor:
            file.write(f'offset_row={anchor[0] if len(anchor)>0 else ""}\n')
            file.write(f'offset_col={anchor[1] if len(anchor)>1 else ""}\n')
            file.write(
                f'offset_pattern={anchor[2] if len(anchor)>2 else ""}\n')
        if line["is_optional"]:
            file.write(f"is_optional=true\n")
        if is_duplicate:
            file.write(f"is_duplicate=true\n")

        if (not is_duplicate and line["name"].find(";") == -1) and line["is_unique"]:
            file.write(f'is_unique=true\n')
