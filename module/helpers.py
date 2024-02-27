import datetime, re, os, json
import pathlib
import hashlib
import zipfile
import logging
import fileinput
from typing import Union
from datetime import datetime
import argparse
from .exceptions import InnMismatchException, FatalException
from .settings import (
    IS_MESSAGE_PRINT,
    POS_NUMERIC_VALUE,
    POS_NUMERIC_IS_ABSOLUTE,
    PATH_CONFIG,
    PATH_TMP,
    ENCONING,
)

logger = logging.getLogger(__name__)


def timing(start_message: str = "", end_message: str = "Завершено"):
    def wrap(f):
        def inner(*args, **kwargs):
            if start_message:
                logger.info(start_message)
            time1 = datetime.now()
            ret = f(*args, **kwargs)
            time2 = datetime.now()
            if end_message:
                logger.info("{0} ({1})".format(end_message, (time2 - time1)))
            return ret

        return inner

    return wrap


def fatal_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InnMismatchException as ex:
            logger.exception("Inn error")
            raise InnMismatchException
        except Exception as ex:
            logger.exception("Fatal error")
            raise FatalException(f"{ex}")

    return wrapper


def warning_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception as ex:
            logger.exception("Warning")
            return None

    return wrapper


def print_message(msg: str, end: str = "\n", flush: bool = False) -> None:
    if IS_MESSAGE_PRINT:
        print(msg, end=end, flush=flush)


def regular_calc(pattern: str, value: str) -> str:
    try:
        result = re.search(
            pattern.replace("||", "|"), value.replace("\n", "").strip(), re.IGNORECASE
        )
        if result is None or result.group(0).find("error") != -1:
            return None
        else:
            return result.group(0).strip()
    except Exception as ex:
        logger.exception("Regular error")
        return f"error in regular: '{pattern}' ({str(ex)})"


def get_index_key(line: str) -> str:
    return re.sub(r"[-.,()+ ]", "", line).lower()


def get_index_find_any(text: str, delimeters: str) -> int:
    a = []
    for item in delimeters:
        index = text.find(item)
        if index != -1:
            a.append(index)
    return min(a) if a else -1


def get_value_str(value: str, pattern: str) -> str:
    return regular_calc(pattern, value)


def get_value_int(value: Union[list, str]) -> int:
    try:
        if value:
            if isinstance(value, list):
                return value[0]
            elif isinstance(value, str):
                return int(value.replace(",", ".").replace(" ", "")).replace(
                    chr(160), ""
                )
        else:
            return 0
    except:
        return 0


def get_value_float(value: str) -> float:
    try:
        if value:
            if isinstance(value, str):
                return float(
                    value.replace(",", ".").replace(" ", "").replace(chr(160), "")
                )
            else:
                return 0
        else:
            return 0
    except:
        return 0


def get_value_range(value: list, count: int = 0) -> list:
    try:
        if value:
            return value
        else:
            return [(i, True) for i in range(count)]
    except:
        return [(i, True) for i in range(count)]


def get_months() -> dict:
    return {
        "январ": "01",
        "феврал": "02",
        "март": "03",
        "апрел": "04",
        "май": "05",
        "мая": "05",
        "июн": "06",
        "июл": "07",
        "август": "08",
        "сентябр": "09",
        "октябр": "10",
        "ноябр": "11",
        "декабр": "12",
    }


def get_absolute_index(items: tuple, current: int) -> int:
    index = (
        items[POS_NUMERIC_VALUE]
        if items[POS_NUMERIC_IS_ABSOLUTE]
        else items[POS_NUMERIC_VALUE] + current
    )
    return index


def getArgs() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", nargs="?")
    parser.add_argument("-i", "--inn", nargs="?")
    parser.add_argument("-c", "--config", nargs="?")
    parser.add_argument("-u", "--union", nargs="?")
    parser.add_argument("-x", "--hash", nargs="?")
    return parser


def remove_files(path: str):
    os.remove(path=path)


def get_path_decoder(path: pathlib.PosixPath) -> str:
    s = [get_name_decoder(x) for x in path.parts[:-1]]
    s += [path.parts[-1]]
    return str(pathlib.Path(*s))


def get_name_decoder(name: str) -> str:
    try:
        return name.encode("cp437").decode("cp866")
    except Exception as ex:
        return name


def get_inn(filename: str) -> str:
    pattern = "[0-9]{10,12}"
    match = re.search(pattern, filename)
    if match:
        return match.group(0)
    return ""


def get_hash_file(file_name: str):
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    md5 = hashlib.md5()

    with open(file_name, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def get_config_files():
    try:
        pattern: re.Pattern = re.compile(r"(?<=gisconfig_)[0-9]{3}")
        files = [x for x in os.listdir(PATH_CONFIG) if pattern.search(x, re.IGNORECASE)]
        # сортировка: 002_05a.ini раньше чем 002_05.ini gisconfig_000_02
        files = sorted(
            files,
            key=lambda x: (
                x[10:13],
                x[14:17] if x[16:17] != "." else x[14:16] + "я",
            ),
        )
        files = [{"name": x, "type": pattern.findall(x)[0]} for x in files]
    except Exception as ex:
        files = []
    return files


def get_list_files(name: str) -> list:
    l = list()
    with open(name, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if line.strip() and line.strip()[0] != ";":
                index = line.find("|")
                if index != -1:
                    line = line[:index]
                index = line.find(";")
                result = []
                if index != -1:
                    try:
                        patt = (
                            r"(?<=;)(?:(?:\s*[0-9]{3}(?:(?:_[0-9]{2}[a-z0-9_]*)|\s*)))?"
                        )
                        result = re.findall(patt, line)
                    except Exception as ex:
                        pass

                    line = line[:index]
                if line.strip():
                    l.append({"file": line.strip(), "inn": "", "config": []})
                    for item in result:
                        if item.strip() == "000":
                            l[-1]["config"].append(item.strip())
                        else:
                            l[-1]["config"].append(
                                f"{PATH_CONFIG}/gisconfig_{item.strip()}.ini"
                                if item.strip()
                                else ""
                            )
    return l


def write_list(path_output: str, files: list):
    os.makedirs(path_output, exist_ok=True)
    mess = ""
    file_output = pathlib.Path(
        path_output, f'session{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
    )
    with open(file_output, "w", encoding=ENCONING) as file:
        b = False
        for item in files:
            for conf in item["config"]:
                if conf["name"] == "":
                    if b is False:
                        mess += "\n\n------------------ Следующие файлы не распознаны ---------------------------------------\n\n"
                        b = True
                    mess += f"{item['inn']} \t {os.path.basename(item['name'])}\n"
                if conf["warning"]:
                    s = " ".join([f"{x}" for x in conf["warning"]]).strip()
                    mess += f"\t{s}\n"
        file.write(mess)
    return file_output if mess else ""


def get_extract_files(
    archive_file: str, extract_dir: str = PATH_TMP, ext: str = r".xls"
) -> list:
    if not os.path.exists(archive_file["file"]):
        return []
    list_files = []
    names = []
    if pathlib.Path(archive_file["file"]).suffix == ".zip":
        with zipfile.ZipFile(archive_file["file"], "r") as zip_file:
            names = [text_file.filename for text_file in zip_file.infolist()]
            for z in names:
                zip_file.extract(z, extract_dir)
    else:
        names.append(archive_file["file"])
    i = 0
    for name in names:
        try:
            old_name = pathlib.Path(extract_dir, name)
            new_name = get_name_decoder(str(old_name))
            s = get_path_decoder(old_name)
            os.rename(s, new_name)
        except Exception as ex:
            pass
        if re.search(ext, new_name):
            conf = archive_file["config"][i] if archive_file.get("config") else ""
            list_files.append(
                get_data_file(
                    {
                        "name": new_name,
                        "inn": archive_file.get("inn", ""),
                        "config": conf,
                        "zip": archive_file.get("file", ""),
                    }
                )
            )
            #     {
            #         "name": new_name,
            #         "inn": archive_file.get("inn", ""),
            #         "config": conf,
            #         "warning": list(),
            #         "zip": archive_file.get("file", ""),
            #     }
            # )
            if i < len(archive_file.get("config", "")) - 1:
                i += 1
    return list_files


def get_data_file(item: dict = None) -> dict:
    return {
        "name": item["name"] if item is not None else "",
        "config": [
            {
                "name": item["config"] if item is not None else "",
                "sheets": [],
                "warning": [],
            }
        ],
        "inn": item["inn"] if item is not None else "",
        "records": None,
        "zip": item["zip"] if item is not None else "",
    }


def hashit(s):
    return hashlib.sha1(s).hexdigest()


def check_tarif(data: list) -> str:
    comp = re.compile(r"[0-9]{1,9}(?:[\.,][0-9]{1,3})?")
    mess = ""
    for index, item in enumerate(data):
        res = comp.findall(item)
        if len(res) != 1:
            mess += f"{index+1}: {item}\n"
    return mess


def get_value(
    value: str = "", pattern: str = "", type_value: str = ""
) -> Union[str, int, float]:
    try:
        value = str(value)
        if type_value == "int":
            value = str(get_value_int(value))
        elif type_value == "double" or type_value == "float":
            value = str(get_value_float(value))
    except:
        pass
    result = regular_calc(pattern, value)
    if result != None:
        try:
            if type_value == "int":
                result = get_value_int(value)
            elif type_value == "double" or type_value == "float":
                result = get_value_float(result)
            else:
                result = result.rstrip() + " "
        except:
            result = 0
    else:
        if type_value == "int":
            result = 0
        elif type_value == "double" or type_value == "float":
            result = 0
        else:
            result = ""
    return result


def write_log_time(file_name: str):
    with open(file_name+".log", "w") as f:
        f.write(f"{file_name}\t" + datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
