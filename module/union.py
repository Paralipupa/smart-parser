from datetime import datetime
import logging
import re
import os
import pathlib
import json
import csv
import zipfile
from typing import NoReturn, Final
from collections import Counter
from .gisconfig import fatal_error, warning_error, PATH_LOG
from .settings import *

# Объединение однотипных файлом


class UnionData:

    def __init__(self) -> None:
        self.logs = list()

    def start(self, path_input: str, path_output: str) -> list:
        save_directories = dict()
        files: list[str] = self.__get_files(path_input)
        if files:
            data = dict()
            del_files = list()
            for file in files:
                for fn in DOCUMENTS.split():
                    inn: list = re.findall(
                        '^[0-9]{8,10}(?=_)', file, re.IGNORECASE)
                    name: list = re.findall(
                        '(?<=[0-9]{1}_)'+fn+'(?=\.json)', file, re.IGNORECASE)
                    period: list = re.findall(
                        '(?<=[0-9]{1}_)[0-9]{2}[0-9]{4}(?=_)', file, re.IGNORECASE)
                    if inn and name and period:
                        del_files.append(file)
                        data.setdefault(inn[0], dict())
                        data[inn[0]].setdefault(f'{name[0]}@{period[0]}', [])
                        data[inn[0]][f'{name[0]}@{period[0]}'].append(
                            self.__get_data(path_input, file))
            for inn, item in data.items():
                for id_period, value in item.items():
                    if len(value) > 1:
                        for key, a in value[0].items():
                            for index in range(1, len(value)):
                                b = value[index].get(key, None)
                                if b:
                                    a = self.__merge(a, b)
                                    value[index].pop(key)
                        for index in range(1, len(value)):
                            value[0].update(value[index])
                    key = self.__write(path_output, inn, id_period, value[0])
                    save_directories[key] = path_output
            for file in del_files:
                os.remove(pathlib.Path(path_input, file))
                os.remove(pathlib.Path(
                    path_input, file.replace('json', 'csv')))
            self.__write_logs()
            return self.__make_archive(path_output, save_directories)
        return []

    def __check_unique(self, file_name: str, arr: list) -> NoReturn:
        setarr = set(arr)
        if len(arr) != len(setarr):
            counter = Counter(arr)
            m = [key for key, x in counter.items() if x > 1]
            self.logs.append(
                f'Найдены не уникальные ключи в {file_name} ({len(m)}) ')
            self.logs.extend(list(map(str, m)))
            print(f'Найдены не уникальные ключи в {file_name} ({len(m)}) ')
            print('\n'.join(map(str, m[:5])))
            if len(m) > 5:
                print('....')

    @fatal_error
    def __get_data(self, path_output: str, file_name: str) -> dict:
        data = dict()
        file_output = pathlib.Path(path_output, file_name)
        with open(file_output, mode='r', encoding=ENCONING) as file:
            data = json.load(file)
            if data:
                # список в словарь
                keys = [x['internal_id'] for x in data]
                self.__check_unique(file_name, keys)
                data = dict(zip(keys, data))
        return data

    @fatal_error
    def __get_files(self, path_output: str) -> list:
        files = list()
        for file in os.listdir(path_output):
            if file.endswith(".json"):
                files.append(file)
        return files

    @warning_error
    def __merge(self, a: dict, b: dict) -> dict:
        for key, valA in a.items():
            valB = b.get(key, None)
            if valB and (not valA or valA != valB):
                if not valA or (valA.replace(' ', '') == valB.replace(' ', '') and len(valA) > len(valB)):
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
    def __make_archive(self, path_output: str, dirs: list) -> str:
        filename_arch = f'output_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.zip'
        arch_zip = zipfile.ZipFile(
            pathlib.Path(path_output, filename_arch), 'w')
        for key, val in dirs.items():
            path = pathlib.Path(val, key)
            for folder, subfolders, files in os.walk(path):
                for file in files:
                    if file.endswith('.csv'):
                        arch_zip.write(os.path.join(
                            folder, file), os.path.join(folder, file), compress_type=zipfile.ZIP_DEFLATED)
        arch_zip.close()
        return filename_arch

    @fatal_error
    def __write_logs(self, num: int = 0) -> NoReturn:
        if len(self.logs) == 0:
            return
        os.makedirs(PATH_LOG, exist_ok=True)
        i = 0
        file_output = pathlib.Path(
            PATH_LOG, f'union_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
        with open(f'{file_output}.log', 'w') as file:
            for log in self.logs:
                file.write(f'{log}\n')
