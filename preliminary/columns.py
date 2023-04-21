import re
from utils import get_ident, get_reg, get_name, get_pattern
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
        for i, line in enumerate(lines["0"]):
            offset = re.findall("{{.+}}", line["name"])
            if offset:
                line["name"] = line["name"].replace(offset[0], "")
                offset = offset[0].replace("{", "").replace("}", "").split(";")
            if line["name"][0] == ">":
                lines["param"]["main_border_column_left"] = [i]
                line["name"] = line["name"][1:]
            if line["name"][0] == "<":
                lines["param"]["main_border_column_right"] = [i]
                line["name"] = line["name"][1:]
            ls = line["name"].split("@")
            line["name"] = ls[0]
            for x in ls[1:]:
                patt = get_pattern(x)
                if patt != "":
                    lines["dic"][x.strip()] = {"col": i, "pattern": patt}
                else:
                    lines["dic"][x.strip()] = {"col": i}
            file.write(f"[col_{i}]\n")
            if i == 0:
                file.write(f"name=ЛС\n")
                file.write(f"condition_begin_team=@ЛС\n")
            else:
                name = get_name(get_ident(line["name"].split(";")[0]), names)
                file.write(f"name={name}\n")
            is_duplicate = False
            for j, x in enumerate(get_reg(line["name"]).split(";")):
                col_off:str = re.sub(r"\(|\)|\+|-|\^|\$|\\|,|\s", "", x)
                if str(col_off).isdigit():
                    col_off:str = re.sub(r"\^|\$|\\", "", x)
                    file.write(
                        f'col_data_offset=+0,{col_off}\n'
                    )
                else:
                    file.write(
                        f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={x}\n'
                    )
                    if not any([y for y in patts if y == x]):
                        patts.append(x)
                    else:
                        is_duplicate = True
            if offset:
                file.write(f'offset_row={offset[0] if len(offset)>0 else ""}\n')
                file.write(f'offset_col={offset[1] if len(offset)>1 else ""}\n')
                file.write(f'offset_pattern={offset[2] if len(offset)>2 else ""}\n')
            if line["is_optional"]:
                file.write(f"is_optional=true\n")
            if is_duplicate:
                file.write(f"is_duplicate=true\n")
            file.write(
                f'is_unique={"true" if not is_duplicate and line["name"].find(";")==-1 else "false"}\n'
            )
            file.write("\n")

        for i, line in enumerate(lines["1"]):
            offset = re.findall("{{.+}}", line["name"])
            if offset:
                line["name"] = line["name"].replace(offset[0], "")
                offset = offset[0].replace("{", "").replace("}", "").split(";")
            index = line["name"].find("@")
            if index != -1:
                lines["dic"][line["name"][index + 1 :].strip()] = {
                    "col": COLUMN_BEGIN + i
                }
                line["name"] = line["name"][:index]
            file.write(f"[col_{COLUMN_BEGIN+i}]\n")
            name = get_name(get_ident(line["name"].split(";")[0]), names)
            file.write(f"name={name}\n")
            is_duplicate = False
            for j, x in enumerate(get_reg(line["name"]).split(";")):
                file.write(
                    f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={x}\n'
                )
                if not any([y for y in patts if y == x]):
                    patts.append(x)
                else:
                    is_duplicate = True
            if not lines["dic"].get("service"):
                if lines["param"].get("main_border_column_left"):
                    file.write(
                        f'border_column_left={lines["param"].get("main_border_column_left", ["2"])[0]}\n'
                    )
                if lines["param"].get("main_border_column_right"):
                    file.write(
                        f'border_column_right={lines["param"].get("main_border_column_right", ["4"])[0]}\n'
                    )
            if offset:
                file.write(f'offset_row={offset[0] if len(offset)>0 else ""}\n')
                file.write(f'offset_col={offset[1] if len(offset)>1 else ""}\n')
                file.write(f'offset_pattern={offset[2] if len(offset)>2 else ""}\n')
            file.write("is_optional=true\n")
            if is_duplicate:
                file.write(f"is_duplicate=true\n")
            if i < len(lines["1"]) - 1:
                file.write("\n")
        if not lines["dic"].get("service"):
            file.write("is_only_after_stable=true\n")
            file.write(f"pattern_0=.+\n")
        file.write("\n")

        if lines["2"]:
            file.write(
                ";--------------------------------------------------------------------------------------------------------------------\n"
            )
        for i, line in enumerate(lines["2"]):
            index = line["name"].find("@")
            if index != -1:
                lines["dic"][line["name"][index + 1 :].strip()] = {
                    "col": COLUMN_BEGIN + i + len(lines["1"])
                }
                line["name"] = line["name"][:index]
            file.write(f'[col_{COLUMN_BEGIN+i+len(lines["1"])}]\n')
            name = get_name(get_ident(line["name"].split(";")[0]), names)
            file.write(f"name={name}\n")
            for j, x in enumerate(get_reg(line["name"]).split(";")):
                file.write(
                    f'pattern{"_" if j >0 else ""}{str(j-1) if j >0 else ""}={x}\n'
                )
            file.write("is_optional=true\n")
        file.write("\n")

        if not lines["dic"].get("service"):
            if lines["3"]:
                file.write(
                    ";--------------------------------------------------------------------------------------------------------------------\n"
                )
                file.write(f'[col_{COLUMN_BEGIN+len(lines["1"])+len(lines["2"])}]\n')
                name = get_name(get_ident(lines["3"][0]["name"].split(";")[0]), names)
                file.write(f"name=Мусор_{name}\n")
                k = 0
                for i, line in enumerate(lines["3"]):
                    for j, x in enumerate(get_reg(line["name"]).split(";")):
                        file.write(
                            f'pattern{"_" if k >0 else ""}{str(k-1) if k >0 else ""}={x}\n'
                        )
                        k += 1
                file.write("is_optional=true\n")
                file.write("is_duplicate=true\n")
        file.write("\n")
    return file_name
