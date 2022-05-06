from ast import Index
import collections
import logging
import re, os
from typing import NoReturn
from file_readers import get_file_reader
from gisconfig import GisConfig
from itertools import product

class ExcelBaseImporter:

    def __init__(self, config_file:str):
        self._is_new_team = False
        self._team = list()        #список областей с данными
        self._headers = list()      #список  записей до табличных данных
        self._names = dict()        #заголовки таблиц
        self._config = GisConfig(config_file)

    def read(self, filename:str, inn:str) -> bool:
        if not self.is_init():
            return False
        self._filename = os.path.basename(filename)
        if not os.path.exists(filename):
            logging.warning('file not found {}. skip'.format(filename))
            return False

        print('Файл {}'.format(self._filename))
        ReaderClass = get_file_reader(filename)
        data_reader = ReaderClass(filename, self.get_page_name(), 0, range(0, self.get_max_cols()), self.get_page_index())
        is_header = True
        names = None
        row = 0
        for record in data_reader:
            self.on_read_line(row,record)
            if is_header:
                if self.get_row_start() + self.get_max_rows_heading() < row:
                    logging.warning('В загружаемом файле "{}" не только лишь все (c) названия колонок найдены: "{}"'
                                    .format(self._filename, ','.join(self._names)))
                    return False
                names = self.get_names(record)
                if self.check_columns(names):
                    self._row_start = row
                is_header = (len(self.get_columns_heading()) > len(self._names))
            else:
                mapped_record = self.map_record(record)
                if mapped_record and self.append_team(mapped_record):
                    self.process_record()
            row += 1
            if row % 100 == 0:
                print('Обработано: {}   \r'.format(row), end='', flush=True)
        self.process_record(True)
        self.done()
        return True

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

