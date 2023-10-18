from utils import get_ident, get_name, get_lines, get_func_name
from settings import *


def write_section_caption(file, sec_type: str):
    n = 80
    file.write(";"+''.rjust(n, "#")+"\n")
    file.write(
        ";"+str(f" {sec_type} ".rjust((n-len(sec_type)-2)//2, "-")).ljust(n, "-")+"\n")
    file.write(";"+''.rjust(n, "#")+"\n")
    file.write('\n')
    return


def write_section_doc(file, sec_type: str, sec_number: int, sec_title: str, sec_name: str, required_fields: str = ""):
    file.write(f'[{sec_type}_{sec_number}]\n')
    file.write(f'; {sec_title}\n')
    file.write(f'name={sec_name}\n')
    if required_fields:
        file.write(f'required_fields={required_fields}\n')
    file.write('\n')
    return


def write_section_org_ppa_guid(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str):
    __write_section_head(file, sec_type, sec_number, sec_title, sec_name)
    file.write('pattern=@\n')
    file.write('col_config=0\n')
    file.write('row_data=0\n')
    file.write('func=inn\n')
    file.write('\n')
    return


def write_section_contract(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str):
    __write_section_head(file, sec_type, sec_number, sec_title, sec_name)
    file.write('pattern=@0\n')
    file.write('col_config=0\n')
    file.write('row_data=0\n')
    file.write('func=_+К,spacerepl,hash\n\n')
    file.write('\n')
    return


def __write_section_service(file, lines: dict, sec_type: str, sec_number: int, sec_title: str,
                            sec_name: str, sec_suffix: str = "", is_ident: bool = True, sec_is_hash: bool = True):
    l: list = get_lines(lines)
    if lines["dic"].get("rr1_puv"):
        file.write('pattern=@0\n')
        file.write('col_config=0\n')
        if lines["dic"].get("service"):
            file.write(
                f'offset_col_config={lines["dic"]["service"][0]["col"]}\n')
            name = get_name(get_ident(l[0]["name"].split(";")[0]))
            file.write(f'offset_pattern=@{name}\n')
        else:
            file.write('row_data=0\n')
        if lines["dic"].get(f"{sec_name}_{sec_type}"):
            if is_ident:
                if sec_suffix:
                    file.write(
                        f'func=id+{get_ident(lines["dic"][f"{sec_name}_{sec_type}"][0]["name"])}+{sec_suffix},spacerepl,hash\n')
                else:
                    file.write(
                        f'func={get_ident(lines["dic"][f"{sec_name}_{sec_type}"][0]["name"])}{",hash" if sec_is_hash else ""}\n')
            else:
                file.write(
                    f'func={get_ident(lines["dic"][f"{sec_name}_{sec_type}"][0]["name"])},hash\n')
        else:
            if is_ident:
                if sec_suffix:
                    file.write(
                        f'func=id+{get_func_name(l[0]["name"].split(";")[0])}+{sec_suffix},spacerepl,hash\n')
                else:
                    file.write(
                        f'func={get_func_name(l[0]["name"].split(";")[0])}{",hash" if sec_is_hash else ""}\n')
            else:
                file.write(
                    f'func={get_func_name(l[0]["name"].split(";")[0])},hash\n')
        if lines["dic"].get(f"{sec_name}_{sec_type}"):
            for i, line in enumerate(lines["dic"][f"{sec_name}_{sec_type}"][1:]):
                file.write(f'[{sec_type}_{sec_number}_{i}]\n')
                file.write(f'; {sec_title}\n')
                if is_ident:
                    if sec_suffix:
                        file.write(
                            f'func=id+{get_ident(line["name"])}+{sec_suffix},spacerepl,hash\n')
                    else:
                        file.write(
                            f'func={get_ident(line["name"])}{",hash" if sec_is_hash else ""}\n')
                else:
                    file.write(
                        f'func={get_ident(line["name"])},hash\n')
        else:
            for i, line in enumerate(l[1:]):
                file.write(f'[{sec_type}_{sec_number}_{i}]\n')
                file.write(f'; {sec_title}\n')
                if lines["dic"].get("service"):
                    name = get_name(
                        get_ident(line["name"].split(";")[0]))
                    file.write(f'offset_pattern=@{name}\n')
                if is_ident:
                    if sec_suffix:
                        file.write(
                            f'func=id+{get_func_name(line["name"].split(";")[0])}+{sec_suffix},spacerepl,hash\n')
                    else:
                        file.write(
                            f'func={get_func_name(line["name"].split(";")[0])}{",hash" if sec_is_hash else ""}\n')
                else:
                    file.write(
                        f'func={get_func_name(line["name"].split(";")[0])},hash\n')
        file.write('\n')
    return


def write_section_internal_id(file, lines: dict, sec_type: str, sec_number: int,
                              sec_title: str, sec_name: str, sec_suffix: str = "",
                              sec_is_service: bool = True, sec_is_hash: bool = True):
    __write_section_head(file, sec_type, sec_number, sec_title, sec_name)
    if sec_is_service:
        __write_section_service(file, lines, sec_type,
                                sec_number, sec_title, sec_name, sec_suffix, sec_is_hash=sec_is_hash)
    else:
        __write_section_internal_id(file)
    return


def write_section_fias(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str, sec_suffix: str = "", sec_is_service: bool = True):
    __write_section_head(file, sec_type, sec_number, sec_title, sec_name)
    file.write('pattern=@0\n')
    file.write('col_config=0\n')
    file.write('row_data=0\n')
    file.write('func=fias\n')
    file.write('func_is_no_return=true\n')
    file.write('\n')
    return


def write_section_address(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str, sec_suffix: str = "", sec_is_service: bool = True):
    __write_section_head(file, sec_type, sec_number, sec_title, sec_name)
    if lines["dic"].get(f"{sec_name}"):
        file.write('pattern=.+\n')
        file.write(
            f'col_config={lines["dic"][f"{sec_name}"][0]["col"]}\n')
        file.write('row_data=0\n')
        if lines["dic"].get("room_number"):
            file.write(
                f'func=_+кв.+column_value({lines["dic"]["room_number"][0]["col"]})\n')
    else:
        file.write(f'col_config=0\n')
        file.write('row_data=0\n')
        file.write('pattern=@0\n')
        if lines["dic"].get("room_number"):
            file.write(
                f'func=address+кв.+column_value({lines["dic"]["room_number"][0]["col"]})\n')
        else:
            file.write(f'func=address\n')
        file.write('func_is_no_return=true\n')
    file.write('\n')
    return


def write_section_account_internal_id(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str):
    __write_section_head(file, sec_type, sec_number, sec_title, sec_name)
    file.write("pattern=@0\n")
    file.write("col_config=0\n")
    file.write("row_data=0\n")
    if lines["dic"].get(f"{sec_name}"):
        file.write(
            f'offset_col_config={lines["dic"][f"{sec_name}"][0]["col"]}\n'
        )
        file.write("offset_pattern=.+\n")
    if lines["dic"].get(f"{sec_name}") and lines["dic"][f"{sec_name}"][0]['func']:
        file.write(
            f'func={lines["dic"][f"{sec_name}"][0]["func"][0]}\n'
        )
    else:
        file.write("func=spacerepl,hash\n")
    file.write("\n")
    return


def write_section_service_internal_id(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str):
    __write_section_head(file, sec_type, sec_number, sec_title, sec_name)
    __write_section_service(file, lines, sec_type, sec_number,
                            sec_title, "internal_id", "ПУ", False)
    return


def write_section_rr(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str, sec_prefix: str = "", sec_suffix: str = "", is_ident: bool = True):
    l = get_lines(lines)
    __write_section_head(file, sec_type, sec_number, sec_title, sec_name)
    if sec_prefix == "":
        sec_prefix = f"_{sec_type}"
    if lines["dic"].get(f"{sec_name}{sec_prefix}") is None:
        sec_prefix = ""
    if lines["dic"].get(f"{sec_name}{sec_prefix}"):
        if lines["dic"].get("service"):
            name = get_name(get_ident(l[0]["name"].split(";")[0]))
            file.write(f'pattern=@{name}\n')
            file.write(f'col_config={lines["dic"]["service"][0]["col"]}\n')
            file.write(
                f'offset_col_config={lines["dic"][f"{sec_name}{sec_prefix}"][0]["col"]}\n')
            file.write('offset_pattern=.+\n')
            file.write('offset_type=float\n')
            file.write('func=round6\n')
            for i, line in enumerate(l[1:]):
                file.write(f'[{sec_type}_{sec_number}_{i}]\n')
                file.write(f'; {sec_title}\n')
                file.write(f'; {line["name"].rstrip()}\n')
                name = get_name(get_ident(line["name"].split(";")[0]))
                file.write(f'pattern=@{name}\n')
        else:
            file.write("pattern=@0\n")
            file.write("col_config=0\n")
            file.write(
                f'offset_col_config={lines["dic"][f"{sec_name}{sec_prefix}"][0]["col"]}\n'
            )
            file.write("offset_pattern=.+\n")
            file.write('offset_type=float\n')
            file.write('func=round6\n')
            for i, line in enumerate(lines["dic"][f"{sec_name}{sec_prefix}"][1:]):
                file.write(f'[{sec_type}_{sec_number}_{i}]\n')
                file.write(f'; {sec_title}\n')
                file.write(
                    f'offset_col_config={line["col"]}\n'
                )
    file.write('\n')
    return


def write_section(file, lines: dict, sec_type: str, sec_number: int, sec_title: str, sec_name: str, sec_prefix: str = "", sec_func: str = ""):
    __write_section_head(file, sec_type, sec_number, sec_title, sec_name)
    if sec_prefix == "":
        sec_prefix = f"_{sec_type}"
    if lines["dic"].get(f"{sec_name}{sec_prefix}") is None:
        sec_prefix = ""
    if lines["dic"].get(f"{sec_name}{sec_prefix}"):
        file.write("pattern=@0\n")
        file.write("col_config=0\n")
        if lines["dic"].get("service") is None:
            file.write("row_data=0\n")
        file.write(
            f'offset_col_config={lines["dic"][f"{sec_name}{sec_prefix}"][0]["col"]}\n'
        )
        if lines["dic"].get(f"{sec_name}{sec_prefix}")[0]['pattern']:
            file.write(
                f'offset_pattern={lines["dic"][f"{sec_name}{sec_prefix}"][0]["pattern"]}\n')
        else:
            file.write("offset_pattern=.+\n")
        if lines["dic"].get(f"{sec_name}{sec_prefix}")[0]['type']:
            file.write(
                f'offset_type={lines["dic"][f"{sec_name}{sec_prefix}"][0]["type"][0]}\n'
            )
        if lines["dic"].get(f"{sec_name}{sec_prefix}")[0]['func']:
            file.write(
                f'func={lines["dic"][f"{sec_name}{sec_prefix}"][0]["func"][0]}\n'
            )
        elif sec_func:
            if sec_func[0] != '!':
                file.write(f"func={sec_func}\n")
            else:
                file.write(f"func={sec_func[1:]}\n")
                file.write(f"func_is_no_return=true\n")
        for i, line in enumerate(lines["dic"][f"{sec_name}{sec_prefix}"][1:]):
            file.write(f'[{sec_type}_{sec_number}_{i}]\n')
            file.write(f'; {sec_title}\n')
            file.write(
                f'offset_col_config={line["col"]}\n'
            )
            if line['func']:
                file.write(
                    f'func={line["func"][0]}\n'
                )
            elif sec_func:
                if sec_func[0] != '!':
                    file.write(f"func={sec_func}\n")
                else:
                    file.write(f"func={sec_func[1:]}\n")
                    file.write(f"func_is_no_return=true\n")
    elif sec_func:
        file.write("pattern=@0\n")
        file.write("col_config=0\n")
        file.write("row_data=0\n")
        if sec_func[0] != '!':
            file.write(f"func={sec_func}\n")
        else:
            file.write(f"func={sec_func[1:]}\n")
            file.write(f"func_is_no_return=true\n")
    file.write('\n')


def __write_section_head(file, sec_type: str, sec_number: int, sec_title: str, sec_name: str):
    file.write(f'[{sec_type}_{sec_number}]\n')
    file.write(f'; {sec_title}\n')
    file.write(f'name={sec_name}\n')
    return


def __write_section_internal_id(file):
    file.write('pattern=@0\n')
    file.write('col_config=0\n')
    file.write('row_data=0\n')
    file.write('func=spacerepl,hash\n\n')
