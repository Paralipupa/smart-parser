import logging
import re
import os
import pathlib
import json
import csv
from typing import NoReturn
from .gisconfig import fatal_error, warning_error
from collections import Counter


db_logger = logging.getLogger('parser')


class UnionData:

    def check_unique(self, file_name: str, arr: list) -> NoReturn:
        setarr = set(arr)
        if len(arr) != len(setarr):
            counter = Counter(arr)
            m = [key for key, x in counter.items() if x > 1]
            print(f'Найдены не уникальные ключи в {file_name} ({len(m)}) ')
            print('\n'.join(map(str, m[:5])))
            if len(m)>5:
                print('....')

    @fatal_error
    def get_data(self, path_output: str, file_name: str) -> dict:
        data = None
        file_output = pathlib.Path(path_output, file_name)
        with open(file_output, mode='r', encoding='utf-8') as file:
            data = json.load(file)
            if data:
                # список в словарь
                keys = [x['internal_id'] for x in data]
                self.check_unique(file_name, keys)
                data = dict(zip(keys, data))
        return data

    @fatal_error
    def get_files(self, path_output: str) -> list:
        files = list()
        for file in os.listdir(path_output):
            if file.endswith(".json"):
                files.append(file)
        return files

    def start(self, path_output: str):
        files = self.get_files(path_output)
        if files:
            data = dict()
            del_files = list()
            for file in files:
                for fn in 'accounts pp pp_charges pu puv'.split():
                    inn = re.findall('^[0-9]{8,10}(?=_)', file, re.IGNORECASE)
                    name = re.findall(
                        '(?<=[0-9]{1}_)'+fn+'(?=\.json)', file, re.IGNORECASE)
                    period = re.findall(
                        '(?<=[0-9]{1}_)[0-9]{4}_[0-9]{2}(?=_)', file, re.IGNORECASE)
                    if inn and name and period:
                        del_files.append(file)
                        data.setdefault(inn[0], dict())
                        data[inn[0]].setdefault(f'{name[0]}_{period[0]}', [])
                        data[inn[0]][f'{name[0]}_{period[0]}'].append(
                            self.get_data(path_output, file))
            for inn, item in data.items():
                for period, value in item.items():
                    if len(value) > 1:
                        for key, a in value[0].items():
                            for i in range(1, len(value)):
                                b = value[i].get(key, None)
                                if b:
                                    a = self.merge(a, b)
                                    value[i].pop(key)
                        for i in range(1, len(value)):
                            value[0].update(value[i])
                    self.write(path_output, inn, period, value[0])
            for file in del_files:
                os.remove(pathlib.Path(path_output, file))
                os.remove(pathlib.Path(
                    path_output, file.replace('json', 'csv')))

    @warning_error
    def merge(self, a: dict, b: dict) -> dict:
        for key, valA in a.items():
            valB = b.get(key, None)
            if valB and (not valA or valA != valB):
                if not valA or (valA.replace(' ', '') == valB.replace(' ', '') and len(valA) > len(valB)):
                    a[key] = valB
        return a

    @fatal_error
    def write(self, path_output: str, inn: str, file_name: str, data: dict) -> NoReturn:
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
