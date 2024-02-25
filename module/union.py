from datetime import datetime
import re
import logging
import os
import pathlib
import json
import csv
import zipfile
import shutil
from collections import Counter
from .helpers import warning_error, fatal_error, print_message
from .exceptions import ConfigNotFoundException
from .settings import *

# Объединение однотипных файлом

logger = logging.getLogger(__name__)


class UnionData:
    def __init__(
        self,
        isParser: bool = True,
        file_log: str = "error.log",
        path_input: str = "input",
        path_output: str = "output",
        file_output: str = "output",
    ):
        self.logs = list()
        self.isParser = isParser
        self.file_log = file_log
        self.path_input = path_input
        self.path_output = path_output
        self.file_output = file_output
        self.exclude = {
            "bill_value",
            "payment_value",
            "credit",
            "saldo",
        }

    def start(self) -> list:
        save_directories = dict()
        is_separate_account_type = True
        files_o: list[str] = self.__get_files()
        files = self.__files_sorted(files_o)
        if files:
            data = self.__get_data_files(files)
            # data = self.__sort_data_files(data)
            for inn, item in data.items():
                for id_period, files in item.items():
                    file_data = {}
                    for file in files:
                        for key_record, record in file.items():
                            if file_data.get(key_record):
                                record = self.__merge(
                                    record, file_data.get(key_record), key_record
                                )
                            if not record.get("account_type") is None:
                                if is_separate_account_type is False:
                                    record.pop("account_type", None)
                                elif record.get("account_type") == "":
                                    record["account_type"] = "uo"
                            file_data[key_record] = record
                    if id_period.find("accounts") != -1:
                        is_separate_account_type = self.__write_account(
                            inn, id_period, file_data, save_directories
                        )
                    else:
                        key = self.__write(inn, id_period, file_data)
                        save_directories[key] = self.path_input
        self.__make_archive(save_directories)
        if os.path.isdir(self.path_input):
            shutil.rmtree(self.path_input)
        return self.file_output

    def __get_data_files(self, files: list) -> dict:
        data = dict()
        self.del_files = list()
        period_current: list = [datetime.now().strftime("%m%Y")]
        period_common: list = period_current
        inn_common: str = ["0000000000"]
        for file in files:
            period_file = re.findall(
                r"(?<=[0-9]{1}_)[0-9]{2}[0-9]{4}(?=_)", file, re.IGNORECASE
            )
            period_common = self.__get_min_period(
                period_a=period_common, period_b=period_file
            )
            inn_file: list = re.findall(r"^[0-9]{8,10}(?=_)", file, re.IGNORECASE)
            if inn_file and inn_file[0] != "0000000000":
                inn_common = inn_file
        period = period_common
        for file in files:
            for fn in DOCUMENTS.split():
                name: list = re.findall(
                    r"(?<=[0-9]{1}_)" + fn + r"(?=\.json)", file, re.IGNORECASE
                )
                if name:
                    inn: list = re.findall(r"^[0-9]{8,10}(?=_)", file, re.IGNORECASE)
                    if inn and inn[0] == "0000000000":
                        inn = inn_common
                    if inn and name and period:
                        self.del_files.append(file)
                        data.setdefault(inn[0], dict())
                        data[inn[0]].setdefault(f"{name[0]}@{period[0]}", [])
                        data[inn[0]][f"{name[0]}@{period[0]}"].append(
                            self.__get_data(file)
                        )
        return data

    def __write_account(
        self,
        inn: str,
        id_period: str,
        file_data: dict,
        save_directories: dict,
    ) -> bool:
        data_files = dict()
        for key, value in file_data.items():
            t = value.get("account_type") if value.get("account_type") else "uo"
            data_files.setdefault(t, {})
            value.pop("account_type", None)
            data_files[t].setdefault(key, value)
        for key, data in data_files.items():
            if len(data_files) > 1:
                file_name, period = id_period.split("@")
                file_name = f"{file_name}_{key}@{period}"
            else:
                file_name = id_period
            key_save = self.__write(inn, file_name, data)
            save_directories[key_save] = self.path_input
        return len(data_files) > 1

    def __check_unique(self, file_name: str, arr: list) -> None:
        setarr = set(arr)
        if len(arr) != len(setarr):
            counter = Counter(arr)
            m = [key for key, x in counter.items() if x > 1]
            self.logs.append(f"Найдены не уникальные ключи в {file_name} ({len(m)}) ")
            self.logs.extend(list(map(str, m)))

    def __sort_data_files(self, data: dict) -> dict:
        try:
            for inn in data.keys():
                for name, value in data[inn].items():
                    value = sorted(value, key=lambda x: -len(x))
        except:
            pass
        finally:
            return data

    @fatal_error
    def __get_data(self, file_name: str) -> dict:
        data = dict()
        file_name = pathlib.Path(self.path_input, file_name)
        with open(file_name, mode="r", encoding=ENCONING) as file:
            try:
                data = json.load(file)
                if data:
                    # список в словарь
                    keys = [x["internal_id"] + x.get("account_type", "") for x in data]
                    self.__check_unique(file_name, keys)
                    data = dict(zip(keys, data))
            except Exception as ex:
                print_message(f"{ex}")
        return data

    @fatal_error
    def __get_files(self) -> list:
        files = list()
        if os.path.isdir(self.path_input):
            for file in os.listdir(self.path_input):
                if file.endswith(".json"):
                    files.append(file)
        return files

    def __files_sorted(self, files_o: list) -> list:
        """Сортировка файлов для обработки
        первым  accounts
        последними banks, tarif
        """
        list_tuple = [
            (
                re.findall("(?<=[0-9]_)[a-z_]+", x)[0],
                int(re.findall("(?<=[0-9]_)[0-9]+", x)[0]),
            )
            for x in files_o
        ]
        list_sorted = sorted(list_tuple)

        files = sorted(
            [
                x
                for x in files_o
                if not re.search("bank", x) and not re.search("tarif", x)
            ],
            key=lambda x: (
                re.findall("(?<=[0-9]_)[a-z_]+", x)[0],
                int(re.findall("(?<=[0-9]_)[0-9]+", x)[0]),
            ),
        )
        files.extend(
            [x for x in files_o if re.search("bank", x) or re.search("tarif", x)]
        )

        return files

    @warning_error
    def __merge(self, a: dict, b: dict, key_record: str) -> dict:
        for key, valA in a.items():
            valB = b.get(key)
            if (
                valB is not None
                and (len(valB.strip()) != 0)
                and ((len(valA.strip()) == 0) or valA != valB)
            ):
                if (len(valA.strip()) == 0) or (
                    len(valA.replace(" ", "")) < len(valB.replace(" ", ""))
                ):
                    # if a[key]:
                    #     logger.debug(f"{key_record} {key}:{a[key]} = {valB}")
                    a[key] = valB
        return a

    @fatal_error
    def __write(self, inn: str, file_with_period: str, data: dict) -> None:
        data = [x for x in data.values()]
        file_name, period = file_with_period.split("@")
        key = f"{inn}_{period}"
        path = pathlib.Path(self.path_input, key)
        os.makedirs(path, exist_ok=True)
        file_name = pathlib.Path(path, file_name)
        with open(f"{file_name}.json", mode="w", encoding=ENCONING) as file:
            jstr = json.dumps(data, indent=4, ensure_ascii=False)
            file.write(jstr)
        with open(f"{file_name}.csv", mode="w", encoding=ENCONING) as file:
            names = [x for x in data[0].keys()]
            file_writer = csv.DictWriter(
                file, delimiter=";", lineterminator="\r", fieldnames=names
            )
            file_writer.writeheader()
            for rec in data:
                file_writer.writerow(rec)
        return key

    @fatal_error
    def __make_archive(self, dirs: list) -> str:
        os.makedirs(self.path_output, exist_ok=True)
        arch_zip = zipfile.ZipFile(
            pathlib.Path(self.path_output, self.file_output), "w"
        )
        if len(dirs) == 0 and self.file_log:
            arch_zip.write(
                self.file_log,
                os.path.basename(self.file_log),
                compress_type=zipfile.ZIP_DEFLATED,
            )
        for key, val in dirs.items():
            path = pathlib.Path(val, key)
            if self.file_log and os.path.exists(self.file_log):
                file_log = pathlib.Path(path, os.path.basename(self.file_log))
                shutil.copy(self.file_log, file_log)
            for folder, _, files in os.walk(path):
                for file in files:
                    name = re.findall(
                        r"(?<=\{0})[0-9a-z_]+$".format(os.path.sep), folder
                    )
                    if name:
                        if file.endswith(".csv") or file.endswith(".log"):
                            arch_zip.write(
                                os.path.join(folder, file),
                                os.path.join(name[0], file),
                                compress_type=zipfile.ZIP_DEFLATED,
                            )
        arch_zip.close()
        return self.file_output

    def __get_min_period(self, period_a: list, period_b: list) -> list:
        if not period_a:
            return period_b
        elif not period_b:
            return period_a
        if period_a[0][2:] < period_b[0][2:]:
            return period_a
        elif period_a[0][2:] > period_b[0][2:]:
            return period_b
        else:
            if period_a[0][:2] < period_b[0][:2]:
                return period_a
            elif period_a[0][:2] > period_b[0][:2]:
                return period_b
            else:
                return period_a
