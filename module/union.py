from datetime import datetime
from collections import defaultdict
import re
import logging
import os
import pathlib
import json
import csv
import zipfile
import shutil
from collections import Counter
from .helpers import (
    warning_error,
    fatal_error,
    print_message,
    get_list_dict_from_csv,
    get_folder,
    write_log_time,
)
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
        is_daemon: bool = False,
        inn: str = "",
    ):
        self.logs = list()
        self.isParser = isParser
        self.file_log = file_log
        self.path_input = path_input
        self.path_output = path_output
        self.file_output = os.path.basename(file_output)
        self.exclude = {
            "bill_value",
            "payment_value",
            "credit",
            "saldo",
        }
        self.is_daemon = is_daemon
        self.dict_ids = {}

    def start(self) -> list:
        save_directories = dict()
        is_separate_account_type = True
        files_o: list[str] = self.__get_files()
        if files_o:
            files_s = self.__files_sorted(files_o)
            period, inn_common = self.__get_commom_data(files_s)
            for index, fn in enumerate(DOCUMENTS.split()):
                if self.is_daemon:
                    # при фоновой обработке отслеживаем процесс выполнения
                    # записывая текущее время в файл
                    write_log_time(
                        os.path.join(self.path_output, self.file_output),
                        False,
                        f"{round(index/len(DOCUMENTS.split()),2)}%",
                    )
                print_message(
                    "         Загрузка: {}                          \r".format(
                        fn,
                    ),
                    end="",
                    flush=True,
                )
                data = self.__get_data_from_files(files_s, period, inn_common, fn)
                if self.is_daemon:
                    # при фоновой обработке отслеживаем процесс выполнения
                    # записывая текущее время в файл
                    write_log_time(
                        os.path.join(self.path_output, self.file_output),
                        False,
                        f"{round(index/len(DOCUMENTS.split()),2)}%",
                    )
                print_message(
                    "         Обработка: {}                          \r".format(
                        fn,
                    ),
                    end="",
                    flush=True,
                )
                for inn, item in data.items():
                    for id_period, files in item.items():
                        file_data = {}
                        if self.is_daemon:
                            # при фоновой обработке отслеживаем процесс выполнения
                            # записывая текущее время в файл
                            write_log_time(
                                os.path.join(self.path_output, self.file_output),
                                False,
                                f"{round(index/len(DOCUMENTS.split()),2)}%",
                            )
                        for file in files:
                            for key_record, record in file.items():
                                try:
                                    if file_data.get(key_record):
                                        record = self.__merge(
                                            record,
                                            file_data.get(key_record),
                                            key_record,
                                        )
                                    if not record.get("account_type") is None:
                                        if is_separate_account_type is False:
                                            record.pop("account_type", None)
                                        elif record.get("account_type") == "":
                                            record["account_type"] = "uo"
                                    file_data[key_record] = record
                                except Exception as ex:
                                    logger.error(f"{ex}")
                                    raise
                        if re.search("^accounts", id_period):
                            is_separate_account_type = self.__write_account(
                                inn, id_period, file_data, save_directories
                            )
                        else:
                            key = self.__write(inn, id_period, file_data)
                            save_directories[key] = self.path_input
            print_message(
                "         Создание архива: {}                          \r".format(
                    fn,
                ),
                end="",
                flush=True,
            )
            self.__make_archive(save_directories)
            if os.path.isdir(self.path_input):
                shutil.rmtree(self.path_input)
                if os.path.isfile(
                    os.path.join(self.path_output, self.file_output + ".log")
                ):
                    os.remove(os.path.join(self.path_output, self.file_output + ".log"))
        return (
            self.file_output
            if os.path.exists(os.path.join(self.path_output, self.file_output))
            else None
        )

    def __get_commom_data(self, files: list):
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
        return period_common, inn_common

    def __get_data_from_files(
        self, files: list, period: list, inn_common: str, fn: str
    ) -> dict:
        data = dict()
        self.del_files = list()
        for file in files:
            name: list = re.findall(
                r"(?<=[0-9]{1}_)" + fn + r"(?=\.)", file, re.IGNORECASE
            )
            if name:
                inn: list = re.findall(r"^[0-9]{8,10}(?=_)", file, re.IGNORECASE)
                if inn and inn[0] == "0000000000":
                    inn = inn_common
                if inn and name and period:
                    self.del_files.append(file)
                    data.setdefault(inn[0], dict())
                    data[inn[0]].setdefault(f"{name[0]}@{period[0]}", [])
                    data[inn[0]][f"{name[0]}@{period[0]}"].append(self.__get_data(file))
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

    def __redefine_data(self, x: dict, keys_redefine: dict):
        for key in keys_redefine:
            key_old = key[2:]
            if x[key]:
                x[key_old] = x[key]
        return x

    def __get_data(self, file_name: str) -> dict:
        """Формируем данные из csv файла"""
        file_name = pathlib.Path(self.path_input, file_name)
        try:
            # данные в виде списка словарей ключ - имя поля
            data = get_list_dict_from_csv(file_name)
            # формируем список ключей прототипов (с двумя __ в начале имени)
            # аналоги которых (имя поля без __) есть в списке полей
            # Например, если присутствуют __internal_id и internal_id,
            # тогда __internal_id добавляем
            keys_redefine = [
                key
                for key in data[0].keys()
                if key[:2] == "__" and data[0].get(key[2:]) is not None
            ]
            # заносим в словарь значения временных полей
            for key in keys_redefine:
                self.dict_ids |= {
                    x[key[2:]]: x[key] for x in data if x.get(key, "").strip()
                }
            # формируем список ключей для каждой строки
            keys = [
                (
                    self.dict_ids.get(x["internal_id"])
                    if self.dict_ids.get(x["internal_id"])
                    else x["internal_id"] + x.get("account_type", "")
                )
                for x in data
            ]

            is_merged = False
            if self.dict_ids:
                # меняем старые значения на новые (из временных полей)
                # для полей у которых были заданы прототипы ( <имя поля> и __<имя поля>)
                for dic in data:
                    for key in keys_redefine:
                        key_old = key[2:]
                        if dic.get(key_old) is not None and self.dict_ids.get(
                            dic.get(key_old)
                        ):
                            dic[key_old] = self.dict_ids.get(dic.get(key_old))
                            if key_old == "internal_id":
                                # если протопит __internal_id, то нужно суммировать числовые поля
                                # из записей соответствующих этом идентификатору
                                is_merged = True
            self.__check_unique(file_name, keys)
            if is_merged:
                # объединяем записи по идентификатрору с суммирование числовых данных
                data = self.merged_data_on_internal_id(keys, data)
            else:
                data = dict(zip(keys, data))
        except Exception as ex:
            logger.error(f"ex")
        return data

    def merged_data_on_internal_id(self, keys, data):
        """объединение записей с одинаковым internal_id с сумирование числовых полей"""
        try:
            merged_data = defaultdict(lambda: defaultdict(float))
            for dic, key in zip(data, keys):
                for field_name, value in dic.items():
                    if self.__is_float(value):
                        if not isinstance(merged_data[key][field_name], float):
                            merged_data[key][field_name] = 0
                        merged_data[key][field_name] += round(float(value), 2)
                        merged_data[key][field_name] = round(
                            merged_data[key][field_name], 2
                        )
                    else:
                        if (
                            field_name not in merged_data[key]
                            or not merged_data[key][field_name]
                        ):
                            merged_data[key][field_name] = value
            data = {
                key: {k: str(v) for k, v in values.items()}
                for key, values in merged_data.items()
            }

        except Exception as ex:
            logger.error(f"{ex}")
        return data

    @fatal_error
    def __get_files(self) -> list:
        """Получить список файлов csv из папки"""
        files = list()
        if not os.path.isdir(self.path_input):
            self.path_input = get_folder(self.path_input)
            if self.path_input:
                self.file_output = os.path.basename(self.path_input) + ".zip"
        if os.path.isdir(self.path_input):
            for file in os.listdir(self.path_input):
                if file.endswith(".csv"):
                    files.append(file)
        return files

    def __is_float(self, value):
        """Определяем число с плавающей точкой с не более 
        чем 2-мя знаками в дробной части"""
        comp: re.compile = re.compile("^-?[0-9]+[.][0-9]{1,2}$")
        try:
            if comp.search(value):
                float(value)
                return True
        except ValueError:
            return False
        return False

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

    def __merge(self, a: dict, b: dict, key_record: str) -> dict:
        """ сравниваем записи с одинаковм идентификатором и записывем по принципу
        чем больше размер, тем лучше """
        try:
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
                        a[key] = valB
        except Exception as ex:
            logger.error(f"{ex}")
        finally:
            return a

    @fatal_error
    def __write(self, inn: str, file_with_period: str, data: dict) -> None:
        """ запись данных в csv файл"""
        data = [x for x in data.values()]
        file_name, period = file_with_period.split("@")
        key = f"{inn}_{period}"
        path = pathlib.Path(self.path_input, key)
        os.makedirs(path, exist_ok=True)
        file_name = pathlib.Path(path, file_name)
        with open(f"{file_name}.csv", mode="w", encoding=ENCONING) as file:
            names = [x for x in data[0].keys() if x[:2] != "__"]
            file_writer = csv.DictWriter(
                file, delimiter=";", lineterminator="\r", fieldnames=names
            )
            file_writer.writeheader()
            for rec in data:
                file_writer.writerow(
                    {key: x for key, x in rec.items() if key[:2] != "__"}
                )
        return key

    @fatal_error
    def __make_archive(self, dirs: list) -> str:
        """ создаем архив zip из csv и log файлов"""
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
                            if not (file == "pu.csv") or (
                                [x for x in files if x == "puv.csv"]
                            ):
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
