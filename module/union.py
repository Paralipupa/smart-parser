from datetime import datetime
import re
import os
import pathlib
import json
import csv
import zipfile
import shutil
from typing import NoReturn
from collections import Counter
from .gisconfig import fatal_error, warning_error, print_message, PATH_LOG
from .exceptions import ConfigNotFoundException
from .settings import *

# Объединение однотипных файлом


class UnionData:

    def __init__(self, isParser:bool, file_log: str) -> None:
        self.logs = list()
        self.isParser = isParser
        self.file_log = file_log

    def start(self, path_input: str, path_output: str, path_logs: str, file_output: str) -> list:
        save_directories = dict()
        files: list[str] = self.__get_files(path_input)
        if files:
            data = dict()
            del_files = list()
            period : list = [datetime.now().strftime('%m%Y')]
            for file in files:
                for fn in DOCUMENTS.split():
                    name: list = re.findall(
                        '(?<=[0-9]{1}_)'+fn+'(?=\.json)', file, re.IGNORECASE)
                    if name:
                        inn: list = re.findall(
                            '^[0-9]{8,10}(?=_)', file, re.IGNORECASE)
                        if not re.search('bank',fn) and not re.search('tarif',fn):
                            period = re.findall(
                                '(?<=[0-9]{1}_)[0-9]{2}[0-9]{4}(?=_)', file, re.IGNORECASE)
                        if inn and name and period:
                            del_files.append(file)
                            data.setdefault(inn[0], dict())
                            data[inn[0]].setdefault(f'{name[0]}@{period[0]}', [])
                            data[inn[0]][f'{name[0]}@{period[0]}'].append(
                                self.__get_data(path_input, file))
            for inn, item in data.items():
                for id_period, files in item.items():
                    file_data = {}
                    for file in files:
                        for key_record, record in file.items():
                            if file_data.get(key_record):
                                record = self.__merge(
                                    record, file_data.get(key_record))
                            file_data[key_record] = record
                    key_record = self.__write(
                        path_input, inn, id_period, file_data)
                    save_directories[key_record] = path_input
            self.__write_logs(path_output=path_logs)
        self.__make_archive(path_output, file_output, save_directories)
        if os.path.isdir(path_input):
            shutil.rmtree(path_input)
        return os.path.join(path_output, file_output) 
        raise ConfigNotFoundException

    def __check_unique(self, file_name: str, arr: list) -> NoReturn:
        setarr = set(arr)
        if len(arr) != len(setarr):
            counter = Counter(arr)
            m = [key for key, x in counter.items() if x > 1]
            self.logs.append(
                f'Найдены не уникальные ключи в {file_name} ({len(m)}) ')
            self.logs.extend(list(map(str, m)))

    @fatal_error
    def __get_data(self, path_output: str, file_name: str) -> dict:
        data = dict()
        file_output = pathlib.Path(path_output, file_name)
        with open(file_output, mode='r', encoding=ENCONING) as file:
            try:
                data = json.load(file)
                if data:
                    # список в словарь
                    keys = [x['internal_id'] for x in data]
                    self.__check_unique(file_name, keys)
                    data = dict(zip(keys, data))
            except Exception as ex:
                print_message(f"{ex}")
        return data

    @fatal_error
    def __get_files(self, path_output: str) -> list:
        files = list()
        if os.path.isdir(path_output):
            for file in os.listdir(path_output):
                if file.endswith(".json"):
                    files.append(file)
        return files

    @warning_error
    def __merge(self, a: dict, b: dict) -> dict:
        for key, valA in a.items():
            valB = b.get(key, None)
            if (len(valB.strip()) != 0) and ((len(valA.strip()) == 0) or valA != valB):
                if (len(valA.strip()) == 0) or (len(valA.replace(' ', '')) < len(valB.replace(' ', ''))):
                    a[key] = valB
        return a

    @fatal_error
    def __write(self, path_output: str, inn: str, file_with_period: str, data: dict) -> NoReturn:
        data = [x for x in data.values()]
        file_name, period = file_with_period.split('@')
        key = f'{inn}_{period}'
        path = pathlib.Path(path_output, key)
        os.makedirs(path, exist_ok=True)
        file_output = pathlib.Path(path, file_name)
        with open(f'{file_output}.json', mode='w', encoding=ENCONING) as file:
            jstr = json.dumps(data, indent=4,
                              ensure_ascii=False)
            file.write(jstr)
        with open(f'{file_output}.csv', mode='w', encoding=ENCONING) as file:
            names = [x for x in data[0].keys()]
            file_writer = csv.DictWriter(file, delimiter=";",
                                         lineterminator="\r", fieldnames=names)
            file_writer.writeheader()
            for rec in data:
                file_writer.writerow(rec)
        return key

    @fatal_error
    def __make_archive(self, path_output: str, filename_arch: str, dirs: list) -> str:
        os.makedirs(path_output, exist_ok=True)
        arch_zip = zipfile.ZipFile(
            pathlib.Path(path_output, filename_arch), 'w')
        if len(dirs) == 0 and self.file_log:
            arch_zip.write(self.file_log, os.path.basename(self.file_log), compress_type=zipfile.ZIP_DEFLATED)
        for key, val in dirs.items():
            path = pathlib.Path(val, key)
            if self.file_log and os.path.exists(self.file_log):
                file_log = os.path.join(path,os.path.basename(self.file_log))
                shutil.copy(self.file_log, file_log)
            for folder, subfolders, files in os.walk(path):
                for file in files:
                    name = re.findall(f'(?<=\{os.path.sep})[0-9a-z_]+$', folder)
                    if name:
                        if file.endswith('.csv') or file.endswith('.log'):
                            arch_zip.write(os.path.join(
                                folder, file), os.path.join(name[0], file), compress_type=zipfile.ZIP_DEFLATED)
        arch_zip.close()
        return filename_arch

    @fatal_error
    def __write_logs(self, num: int = 0, path_output: str = 'logs') -> NoReturn:
        if len(self.logs) == 0:
            return
        os.makedirs(path_output, exist_ok=True)
        i = 0
        file_output = pathlib.Path(
            path_output, f'union_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
        with open(f'{file_output}.log', 'w', encoding=ENCONING) as file:
            for log in self.logs:
                file.write(f'{log}\n')
