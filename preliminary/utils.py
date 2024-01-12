import fileinput
import re
from typing import Tuple


def set_lines() -> list:
    return {
        "0": [],
        "1": [],
        "1a": [],
        "2": [],
        "2a": [],
        "3": [],
        "9": [],
        "param": {},
        "dic": {},
        "required": {},
    }


def set_parameters() -> list:
    return ["name", "border_column_left", "border_column_right"]


def get_ident(name: str) -> str:
    result = "".join(c for c in name.title() if c.isalnum())
    result = result.replace("Итого ", "")
    return result


def get_reg(pattern: str) -> str:
    new_pattern = ''
    for patt in pattern.split(";"):
        if patt and not patt[0] in ("+-("):
            patt = patt.replace("\\", "\\\\").replace("/", "\/")
            patt = patt.replace("[", "\[").replace("]", "\]")
            patt = patt.replace("(", "\(").replace(")", "\)")
            patt = patt.replace(".", "[.]").replace("*", "[*]")
            patt = patt.replace("+", "[+]").replace("_", "")
        new_pattern += (patt + ";")
    new_pattern = new_pattern.strip(";").strip()
    return (
        f'^{new_pattern.rstrip().replace(";","$;^")}$'
        if new_pattern.find("^") == -1 and new_pattern.find("$") == -1
        else new_pattern.rstrip()
    )


def get_name(name: str, names: list = None) -> str:
    if names is not None:
        j = 0
        while any([x for x in names if x == (name if j == 0 else f"{name}_{j}")]):
            j += 1
        name = name if j == 0 else f"{name}_{j}"
        names.append(name)
    return name


def get_lines(lines: list) -> list:
    l = []
    if len(lines["1a"]) == 0 and len(lines["2a"]) == 0:
        ll = lines["1"][-1:]
        l.extend(lines["1"][:-1])
        l.extend(lines["2"])
    else:
        ll = lines["1a"][-1:]
        l.extend(lines["1a"][:-1])
        l.extend(lines["2a"])
    l = sorted(l, key=lambda x: x["name"])
    l.extend(ll)
    return l


def write_config(filenames: list, path: str, output: str = "gis_config.ini"):
    file_name = f"{path}/ini/{output}"
    with open(file_name, "w") as fout, fileinput.input(filenames) as fin:
        for line in fin:
            fout.write(line)


def sorted_lines(lines: list) -> list:
    lines["1"] = sorted(lines["1"], key=lambda x: x["name"])
    lines["2"] = sorted(lines["2"], key=lambda x: x["name"])
    lines["3"] = sorted(lines["3"], key=lambda x: x["name"])
    lines["1a"] = sorted(lines["1a"], key=lambda x: x["name"])
    lines["2a"] = sorted(lines["2a"], key=lambda x: x["name"])
    return lines


def get_param_anchor(x: str) -> Tuple[str, list]:
    anchor = re.findall("{{.+}}", x)
    if anchor:
        # проверяем наличие "якоря"
        x = x.replace(anchor[0], "")
        anchor = anchor[0].replace("{", "").replace("}", "").split(";")
    return x, anchor

def get_param_offset(x: str) -> Tuple[str, list]:
    param_off = re.findall('{offset{.+\}}', x)
    if param_off:
        x = x.replace(param_off[0], "")
        param_off[0] = param_off[0].replace("{offset{", "").replace("}}", "")
    return x, param_off

def get_param_function(x: str) -> Tuple[str, list]:
    param_func = re.findall('{func{.+}}', x)
    if param_func:
        x = x.replace(param_func[0], "")
        param_func[0] = param_func[0].replace(
            "{func{", "").replace("}}", "")
    return x, param_func

def get_param_function_is_no_return(x: str) -> Tuple[str, list]:
    param_func_is_no = re.findall('{func_no{.+}}', x)
    if param_func_is_no:
        x = x.replace(param_func_is_no[0], "")
        param_func_is_no[0] = param_func_is_no[0].replace(
            "{func_no{", "").replace("}}", "")
    return x, param_func_is_no

def get_param_type(x: str) -> Tuple[str, list]:
    param_type = re.findall('{type{.+}}', x)
    if param_type:
        x = x.replace(param_type[0], "")
        param_type[0] = param_type[0].replace(
            "{type{", "").replace("}}", "")
    return x, param_type


def get_pattern(x: str, default: str = '') -> Tuple[str, str]:
    index = x.find("::")
    pattern =  (x[index + 2:] if index != -1 else default).replace(r"^Прочие$", ".+")
    if pattern and pattern[0] == "!":
        pattern = "@" + pattern[1:]
    x = x.replace('::'+pattern, '').strip()
    return x, pattern

def get_func_name(x: str) -> str:
    return re.sub("[\^\$\+]","",x.replace(","," ").rstrip())
