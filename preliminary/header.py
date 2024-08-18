import re
from utils import get_ident, get_reg, get_name, get_pattern
from settings import *


def header(lines: list, path: str) -> str:
    patts = []
    names = []
    file_name = f"{path}/ini/0_header.ini"
    with open(file_name, "w") as file:
        file.write(
            f';--------------- {lines["param"].get("name",[""])[0] } ----------------\n'
        )
        file.write("[check]\n")
        file.write(
            "; Поиск ключевого значения по строке(ам) для определения совместимости\n"
        )
        file.write("; входных данных и конфигурации\n")
        file.write(f"row={lines['param'].get('check_row',['0<15'])[0]}\n")
        if lines["param"].get("check_pattern"):
            for i, p in enumerate(lines["param"]["check_pattern"]):
                _, pattern = get_pattern(p, p)
                file.write(
                    f'pattern{"_" if i>0 else ""}{i-1 if i>0 else ""}={pattern}\n'
                )

        file.write("\n")

        file.write("[main]\n")
        if lines['param'].get('filetype'):
            file.write(f"file_type={lines['param'].get('filetype')[0]}\n")
        file.write(
            f"path_output={lines['param'].get('main_path_output',['output'])[0]}\n"
        )
        file.write(f"row_start={lines['param'].get('main_row_start',['0'])[0]}\n")
        file.write(f"page_name={lines['param'].get('main_page_name',[''])[0]}\n")
        file.write(f"page_names={lines['param'].get('main_page_names',[''])[0]}\n")
        file.write(f"page_index={lines['param'].get('main_page_index',['0'])[0]}\n")
        file.write(f"max_columns={lines['param'].get('main_max_columns',[150])[0]}\n")
        file.write(
            f"max_rows_heading={lines['param'].get('main_max_rows_heading',[15])[0]}\n"
        )
        if lines["param"].get("main_border_column_left"):
            file.write(
                f'border_column_left={lines["param"]["main_border_column_left"][0]}\n'
            )
        if lines["param"].get("main_border_column_right"):
            file.write(
                f'border_column_right={lines["param"]["main_border_column_right"][0]}\n'
            )
        if lines["dic"].get("checking_rows"):
            file.write(
                f'checking_rows={lines["dic"]["checking_rows"][0]["name"]}::{lines["dic"]["checking_rows"][0]["pattern"]}\n'
            )

        file.write("\n")

        file.write(";---- шаблоны регулярных выражений ------------\n\n")
        file.write("[pattern]\n")
        file.write("name=currency\n")
        if lines["param"].get("pattern_currency"):
            file.write(f"pattern={lines['param'].get('pattern_currency')}\n")
        else:
            file.write("pattern=^-?\d{1,7}(?:[\.,]\d{1,3})?$\n")
        file.write("\n")

        k = 0
        for key, val in lines["param"].items():
            if key[:8] == "pattern_":
                file.write(f"[pattern_{k}]\n")
                file.write(f"name={key[8:]}\n")
                for i, p in enumerate(val):
                    index = p.find("@")
                    if index > 0:
                        file.write(
                            f'pattern{"_" if i>0 else ""}{i-1 if i>0 else ""}={p[:index] if index != -1 else p }\n'
                        )
                        fields = p[index+1:]
                    else:
                        file.write(
                            f'pattern{"_" if i>0 else ""}{i-1 if i>0 else ""}={p}\n'
                        )
                file.write("\n")
                k += 1

        if not lines["param"].get("pattern_timezone"):
            file.write(f"[pattern_{k}]\n")
            file.write("name=timezone\n")
            file.write("pattern=@+3\n")
            file.write("\n")
            k += 1

        k = 0
        for i, line in enumerate(lines["1"], k):
            name = line["name"].split(";")[0]
            if not name in names:
                k += 1
                file.write(f"[pattern_{COLUMN_BEGIN+i}]\n")
                name = get_name(get_ident(name), names)
                file.write(f"name={name}\n")
                for j, x in enumerate(get_reg(line["name"]).split(";")):
                    _, pattern = get_pattern(x, x)
                    file.write(
                        f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={pattern}\n'
                    )
                    file.write("\n")

        for i, line in enumerate(lines["2a"], k):
            name = line["name"].split(";")[0]
            if not name in names:
                k += 1
                file.write(f"[pattern_{COLUMN_BEGIN+i}]\n")
                name = get_name(get_ident(name), names)
                file.write(f"name={name}\n")
                for j, x in enumerate(get_reg(line["name"]).split(";")):
                    _, pattern = get_pattern(x, x)
                    file.write(
                        f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={pattern}\n'
                    )
                    file.write("\n")

        for i, line in enumerate(lines["1a"], k):
            name = line["name"].split(";")[0]
            if not name in names:
                k += 1
                file.write(f"[pattern_{COLUMN_BEGIN+i}]\n")
                name = get_name(get_ident(name), names)
                file.write(f"name={name}\n")
                for j, x in enumerate(get_reg(line["name"]).split(";")):
                    _, pattern = get_pattern(x, x)
                    file.write(
                        f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={pattern}\n'
                    )
                    file.write("\n")
        file.write("\n")

        file.write(
            ";--------------------------------------------------- параметры --------------------------------------------------\n\n"
        )
        k = 0
        for key, val in lines["param"].items():
            if key[:8] == "pattern_":
                file.write(f"[headers_{k}]\n")
                file.write(f"name={key[8:]}\n")
                file.write(f"pattern=@{key[8:]}\n")
                for i, p in enumerate(val):
                    if p == "":
                        file.write(f"value=\n")
                    else:
                        index = p.find("@")
                        if index != -1:
                            file.write(f"value={p[index+1:]}\n")
                file.write("\n")
                k += 1
            elif key[:7] == "header_":
                file.write(f"[headers_{k}]\n")
                file.write(f"name={key[7:]}\n")
                for i, p in enumerate(val):
                    index = p.find("@")
                    if index != -1:
                        if index > 0:
                            file.write(f"pattern={p[:index]}\n")
                        file.write(f"func={p[index+1:]}\n")
                    else:
                        file.write(f"pattern={p[:index]}\n")

                file.write("\n")
                k += 1

        if not lines["param"].get("pattern_timezone"):
            file.write(f"[headers_{k}]\n")
            file.write("name=timezone\n")
            file.write("pattern=@timezone\n\n")
            k += 1

    return file_name
