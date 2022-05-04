import collections
import logging
import re, os
from typing import NoReturn

from file_readers import get_file_reader


class ExcelBaseImporter:

    file_name = ""
    names = dict()
    collections = list()


    def __init__(self, max_cols, page_index, page_name, collection, cleanup_table, start_row=0):
        self._max_cols = max_cols
        self._page_index = page_index
        self._page_name = page_name
        self._collection = collection
        self._cleanup_table = cleanup_table
        self._start_row = start_row
        self._condition_range = '(.)*'
        self._columns_def = ''

    def read(self, file_path):
        self.file_name = os.path.basename(file_path)
        if not os.path.exists(file_path):
            logging.warning('file not found {}. skip'.format(self.file_name))
            return
        if self._collection:
            self._collection.create_index('internal_id')
            if self._cleanup_table:
                self._collection.delete_many({'file_name': self.file_name})

        print("Файл {}".format(self.file_name))
        ReaderClass = get_file_reader(file_path)
        data_reader = ReaderClass(file_path, self._page_name, 0, range(0, self._max_cols), self._page_index)
        is_header = True
        names = None
        index = 0
        for record in data_reader:
            self.on_read_line(index,record)
            if index >= self._start_row:
                if is_header:
                    names = self.get_names(record)
                    self.check_columns(names)
                    is_header = (len(self.get_columns_def()) > len(self.names))
                else:
                    mapped_record = self.map_record(record)
                    if mapped_record:
                        self.process_record(mapped_record)
            index = index + 1
            if index % 100 == 0:
                print("Обработано: {}   \r".format(index), end='', flush=True)
        self.done()

    def done(self):
        pass

    def set_columns_def(self, value) -> NoReturn:
        self._columns_def = value

    def get_columns_def(self) -> list:
        if self._columns_def:
            return self._columns_def
        else:
            raise Exception("Должен быть определен в наследниках")

    def get_optional_columns_def(self):
        return []

    def set_condition_range(self, value: str) -> NoReturn:
        self._condition_range = value

    def get_condition_range(self) -> str:
        return self._condition_range

    def map_record(self, record):
        result_record = {}
        is_empty = True
        for c in self.get_columns_def():
            v = record[self.get_index(self.names, c)]
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
        return next((index for name, index in names.items() if name == col_name), -1)

    def check_columns(self, names):
        result = dict()
        for c in self.get_columns_def():
            index = self.get_index(names, c)
            if index != -1:
                result[c] = index
        if len(result) > 0:
            self.names.update(result)
            
        #         result.add(c)
        # if len(result) > 0:
        #     raise Exception("В загружаемом файле {} не найдены поля: [{}]".format(file_name, ",".join(result)))

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
        if is_bound or len(self.collections) == 0:
            self.collections.append(mapped_record)
        else:
            for key, value in mapped_record.items():
                self.collections[-1][key].append(value[0])


    def on_read_line(self, index, record):
        pass
