import collections
import logging
import re, os
from typing import NoReturn

from file_readers import get_file_reader


class ExcelBaseImporter:

    def __init__(self):
        self._row_start = 0
        self._documents = list()
        self._names = dict()
        self._condition_range = '(.)*'
        self._columns_def = ''
        self._page_name = ''
        self._page_index = 0
        self._max_cols = 20

    def read(self, filename:str, inn:str='0000000000') -> bool:
        self._filename = os.path.basename(filename)
        if not os.path.exists(filename):
            logging.warning('file not found {}. skip'.format(self._filename))
            return False

        print("Файл {}".format(self._filename))
        ReaderClass = get_file_reader(filename)
        data_reader = ReaderClass(filename, self._page_name, 0, range(0, self._max_cols), self._page_index)
        is_header = True
        names = None
        index = 0
        for record in data_reader:
            self.on_read_line(index,record)
            if is_header:
                if self._row_start + 20 < index:
                    logging.warning("В загружаемом файле '{}' не только лишь все названия колонок найдены: '{}'"
                                    .format(self._filename, ",".join(self._names)))
                    return False
                names = self.get_names(record)
                if self.check_columns(names):
                    self._row_start = index
                is_header = (len(self.get_columns_def()) > len(self._names))
            else:
                mapped_record = self.map_record(record)
                if mapped_record:
                    self.process_record(mapped_record)
            index = index + 1
            if index % 100 == 0:
                print("Обработано: {}   \r".format(index), end='', flush=True)
        self.done()
        return True

    def done(self):
        pass

    def set_columns_def(self, value) -> NoReturn:
        self._columns_def = value

    def get_columns_def(self) -> list:
        if self._columns_def:
            return self._columns_def
        else:
            raise Exception("Должен быть определен в наследниках")

    def set_condition_range(self, value: str) -> NoReturn:
        self._condition_range = value

    def get_condition_range(self) -> str:
        return self._condition_range

    def map_record(self, record):
        result_record = {}
        is_empty = True
        for c in self.get_columns_def():
            v = record[self.get_index(self._names, c)]
            is_empty = is_empty and (v == '' or v is None)
            result_record[c] = [v]
        return result_record if not is_empty else None

    def get_names(self, record):
        names = {}
        index = 0
        for cell in record:
            if cell:
                names[str(cell).strip()] = index
            index += 1
        return names

    def get_index(self, names, col_name):
        return next((index for name, index in names.items() if re.search(col_name,name)), -1)

    def check_columns(self, names : list) -> bool:
        result = dict()
        for c in self.get_columns_def():
            index = self.get_index(names, c)
            if index != -1:
                result[c] = index
        if len(result) > 0:
            self._names.update(result)
            return True
        return False
            
    def check_column_duplicates(self, file_name, names):
        dups = list([item for item, count in collections.Counter(names.values()).items() if count > 1])
        if len(dups) > 0:
            raise Exception("В загружаемом файле {} найдены дублирующиеся названия колонок: {}"
                            .format(file_name, ",".join(dups)))

    def process_record(self, mapped_record):
        reg = self.get_condition_range()
        is_bound = False
        for value in mapped_record.values():
            match = re.search(reg, value[0]) 
            if match:
                is_bound = True
                break
        if is_bound or len(self._documents) == 0:
            self._documents.append(mapped_record)
        else:
            for key, value in mapped_record.items():
                self._documents[-1][key].append(value[0])


    def on_read_line(self, index, record):
        pass
