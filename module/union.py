from datetime import datetime
import logging
import re
import os
import pathlib
import json
import csv
from typing import NoReturn, Final
from collections import Counter
from .gisconfig import fatal_error, warning_error, PATH_LOG

db_logger = logging.getLogger('parser')
DOCUMENTS: Final = 'accounts pp pp_charges pu puv'

# Объединение однотипных файлом


class UnionData:

    def __init__(self) -> None:
        self.logs = list()

    def start(self, path_output: str) -> NoReturn:
        files: list[str] = self.__get_files(path_output)
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
                        '(?<=[0-9]{1}_)[0-9]{4}_[0-9]{2}(?=_)', file, re.IGNORECASE)
                    if inn and name and period:
                        del_files.append(file)
                        data.setdefault(inn[0], dict())
                        data[inn[0]].setdefault(f'{name[0]}_{period[0]}', [])
                        data[inn[0]][f'{name[0]}_{period[0]}'].append(
                            self.__get_data(path_output, file))
            for inn, item in data.items():
                for period, value in item.items():
                    if len(value) > 1:
                        for key, a in value[0].items():
                            for index in range(1, len(value)):
                                b = value[index].get(key, None)
                                if b:
                                    a = self.__merge(a, b)
                                    value[index].pop(key)
                        for index in range(1, len(value)):
                            value[0].update(value[index])
                    self.__write(path_output, inn, period, value[0])
            for file in del_files:
                os.remove(pathlib.Path(path_output, file))
                os.remove(pathlib.Path(
                    path_output, file.replace('json', 'csv')))
            self.__write_logs()

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
        with open(file_output, mode='r', encoding='utf-8') as file:
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
    def __write(self, path_output: str, inn: str, file_name: str, data: dict) -> NoReturn:
        data = [x for x in data.values()]
        file_output = pathlib.Path(path_output, f'{inn}_{file_name}')
        with open(f'{file_output}.json', mode='a', encoding='utf-8') as file:
            jstr = json.dumps(data, indent=4,
                              ensure_ascii=False)
            file.write(jstr)
        with open(f'{file_output}.csv', mode='a', encoding='utf-8') as file:
            names = [x for x in data[0].keys()]
            file_writer = csv.DictWriter(file, delimiter=";",
                                         lineterminator="\r", fieldnames=names)
            file_writer.writeheader()
            for rec in data:
                file_writer.writerow(rec)

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
