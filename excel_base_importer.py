from ast import Index
from asyncore import write
import collections
import logging
import re, os
from typing import NoReturn
from file_readers import get_file_reader
from gisconfig import GisConfig
from itertools import product
import json
import pickle

class ExcelBaseImporter:

    def __init__(self, file_name:str, inn:str, config_file:str):
        self._is_new_team = False
        self._team = list()        #список областей с данными
        self._headers = list()     #список  записей до табличных данных
        self._names = dict()       #заголовки таблиц
        self._parameters = dict()   #данные отчета (период, и др.) 
        self._parameters['filename'] = [file_name]
        self._parameters['inn'] = [inn]
        self._parameters['config'] = [config_file]
        self._collections = dict() #коллекция таблиц БД 
        self._config = GisConfig(config_file)

    def read(self) -> bool:
        if not self.is_init():
            return False

        if not os.path.exists(self._parameters['filename'][0]):
            logging.warning('file not found {}. skip'.format(self._parameters['filename'][0]))
            return False

        print('Файл {}'.format(self._parameters['filename'][0]))
        ReaderClass = get_file_reader(self._parameters['filename'][0])
        data_reader = ReaderClass(self._parameters['filename'][0], self.get_page_name(), 0, range(0, self.get_max_cols()), self.get_page_index())
        is_header = True
        names = None
        row = 0
        for record in data_reader:
            self.on_read_line(row,record)
            if is_header:
                if self.get_row_start() + self.get_max_rows_heading() < row:
                    logging.warning('В загружаемом файле "{}" не только лишь все (c) названия колонок найдены: "{}"'
                                    .format(self._parameters['filename'][0], ','.join(self._names)))
                    return False
                names = self.get_names(record)
                if self.check_columns(names):
                    self._row_start = row
                is_header = (len(self.get_columns_heading()) > len(self._names))
                if not is_header:
                    self._set_parameters()
            else:
                mapped_record = self.map_record(record)
                if mapped_record and self.append_team(mapped_record):
                    if len(self._team) > 1:
                        self.process_record(self._team[-2])
            row += 1
            if row % 100 == 0:
                print('Обработано: {}   \r'.format(row), end='', flush=True)
        if len(self._team) !=0 :
            self.process_record(self._team[-1])
        self.done()
        return True

    def write(self):
        if not self.is_init():
            return False

        path = 'output'
        os.makedirs(path,exist_ok=True)
        for name, records in self._collections.items():
            with open(f'{path}/{name}.csv', 'w') as file:
                file.write(f'{{')
                for key, value in self._parameters.items():
                    file.write(f'\t{key}:[')
                    for val in value:
                        file.write(f'{val} ')
                    file.write(f'],\n')
                file.write(f'}},\n')

                for rec in records:
                    file.write(f'{{\n')
                    for fld_name, values in rec.items():
                        file.write(f'\t{fld_name}:[')
                        for val in values:
                            file.write(f'{val} ')
                        file.write(f'],\n')
                    file.write(f'}},\n')

                                            

    def done(self):
        pass

    def map_record(self, record):
        result_record = {}
        is_empty = True
        for key, index in self._names.items():
            v = record[index['col']]
            is_empty = is_empty and (v == '' or v is None)
            result_record[key] = [v]
        return result_record if not is_empty else None

    def get_names(self, record) -> dict:
        names = {}
        index = 0
        self._headers.append(record)
        for cell in record:
            if cell:
                names[str(cell).strip()] = index
            index += 1
        return names

    def get_index(self, names:list, col_name:str) -> int:
        return next((index for name, index in names.items() if name == col_name), -1)

    def check_columns(self, names:list) -> bool:
        result = dict()
        index = 0
        for c in self.get_columns_heading():
            col = self.get_index(names, c)
            if col != -1:
                b, c = self.check_columns_offset(c,col)
                if b:
                    result[c] = {'index':index, 'col': col}
            index += 1
        if len(result) > 0:
            self._names.update(result)
            return True
        return False

    # Проверка на наличие 'якоря' (текста смещенного относительно позиции текущей ячейки)
    def check_columns_offset(self, key:str, index:int) -> bool:
        dic = self.get_columns_heading_offset(key)
        if dic and dic['text']:
            rows = [i-1 for i in dic['row']]
            cols = dic['col']
            for row, col in product(rows,cols):                
                if self._headers[row][index+col] == dic['text']:
                    return True, (dic['text'] + ' ' + key if dic['is_include'] else key)
            return False, key
        return True, key


    def check_column_duplicates(self, file_name:str, names:list):
        dups = list([item for item, count in collections.Counter(names.values()).items() if count > 1])
        if len(dups) > 0:
            raise Exception('В загружаемом файле {} найдены дублирующиеся названия колонок: {}'
                            .format(file_name, ','.join(dups)))

    def append_team(self, mapped_record:list) -> bool:
        match = re.search(self.get_condition_team(), mapped_record[self.get_condition_column()][0])
        if match or len(self._team) == 0:
            self._team.append(mapped_record)
            return True
        else:
            self._is_new_team = False
            for key, value in mapped_record.items():
                self._team[-1][key].append(value[0])
            return False

    def _set_parameters(self):
        rows = self._config._parameters['period']['row']
        cols = self._config._parameters['period']['col']
        pattern = self._config._parameters['period']['pattern']
        self._parameters.setdefault('period',list())
        for row, col in product(rows,cols):           
            result = re.findall(pattern, self._headers[row][col])
            if result:
                for item in result:
                    self._parameters['period'].append(item)

    def process_record(self):
        pass

    def on_read_line(self, index, record):
        pass

# ---------- Параметры конфигурации --------------------
    def is_init(self) -> bool:
        return self._config._is_init

    def get_columns_heading(self) -> list:
        return self._config._columns_heading

    def get_columns_heading_offset(self, key:str) -> dict:
        index = self._config._columns_heading.index(key)
        if index != -1:
            return self._config._columns_heading_offset[index]
        return None

    def get_condition_team(self) -> str:
        return self._config._condition_team

    def get_condition_column(self) -> str:
        return self._config._condition_column

    def get_page_name(self) -> str:
        return self._config._page_name

    def get_page_index(self) -> int:
        return self._config._page_index

    def get_max_cols(self) -> int:
        return self._config._max_cols

    def get_row_start(self) -> int:
        return self._config._row_start

    def get_max_rows_heading(self) -> int:
        return self._config._max_rows_heading

