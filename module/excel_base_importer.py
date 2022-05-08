import collections
import logging
import re, os, hashlib, datetime
from typing import NoReturn
from module.file_readers import get_file_reader
from module.gisconfig import GisConfig
from itertools import product
import uuid

_hashit = lambda s: hashlib.sha1(s).hexdigest()

class ExcelBaseImporter:

    def __init__(self, file_name:str, inn:str, config_file:str):
        self._team = list()        #список областей с данными
        self._headers = list()     #список  записей до табличных данных
        self._names = dict()       #заголовки таблиц
        self._parameters = dict()   #параметры отчета (период, и др.)
        self._parameters['filename'] = [file_name]
        self._parameters['inn'] = [inn]
        self._parameters['config'] = [config_file]
        self._collections = dict() #коллекция выходных таблиц
        self._config = GisConfig(config_file)

    def read(self) -> bool:
        if not self.is_init():
            return False

        if not os.path.exists(self._parameters['filename'][0]):
            logging.warning('file not found {}. skip'.format(self._parameters['filename'][0]))
            return False

        print('Файл {}'.format(self._parameters['filename'][0]))
        ReaderClass = get_file_reader(self._parameters['filename'][0])
        data_reader = ReaderClass(self._parameters['filename'][0], self.get_page_name(), 0, range(self.get_max_cols()), self.get_page_index())
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
                    self.set_parameters()
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

    # Проверка на наличие 'якоря' (текста, смещенного относительно позиции текущего заголовка)
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
        if match: # or len(self._team) == 0:
            self._team.append(mapped_record)
            return True
        elif len(self._team) != 0:
            for key, value in mapped_record.items():
                self._team[-1][key].append(value[0])
            return False

    def set_parameters(self) -> NoReturn:
        self.set_period()

    def set_period(self):
        rows = self._config._parameters['period']['row']
        cols = self._config._parameters['period']['col']
        pattern:str = self._config._parameters['period']['pattern']
        self._parameters.setdefault('period',list())
        if pattern:
            if pattern[0] == '@':
                self._parameters['period'].append(pattern[1:])
            else:
                for row, col in product(rows,cols):
                    result = re.findall(pattern, self._headers[row][col])
                    if result:
                        for item in result:
                            self._parameters['period'].append(item)
        if len(self._parameters['period']) == 0:
            self._parameters['period'].append(datetime.date.today())


    def process_record(self, team:dict) -> NoReturn:
        pass

    def on_read_line(self, index, record):
        pass

    def get_key(self, index:int) -> str:
        for key, value in self._names.items():
            if value['index'] == index:
                return key
        return ''

    def get_value_str(self, value:str, pattern:str) -> str:
        result = re.search(pattern, value)
        if result:
            return result.group(0)
        return ''

    def get_value_int(self, value:list) -> int:
        if value and isinstance(value, list):
            return value[0]
        else:
            return 0

    def get_value_range(self, value:list, count:int=0) -> list:
        try:
            if value:
                return value
            else:
                return range(count)
        except:
            return range(count)

# ---------- Документы --------------------

    def append_to_collection(self, name:str, doc:dict) -> NoReturn:
        self._collections.setdefault(name, list())
        self._collections[name].append(doc)

    def get_document(self, team:dict, doc_param):
        doc = dict()
        count = 0
        for item_fld  in doc_param['fields']:
            doc.setdefault(item_fld['name'], list())
            key = self.get_key(self.get_value_int(item_fld['column']))
            if key and item_fld['pattern']:
                rows = self.get_value_range(item_fld['row'], len(team[key]))
                for row in rows:
                    if len(team[key]) > row and team[key][row]:
                        value = self.get_value_str(team[key][row], item_fld['pattern'] )
                        if value:
                            if item_fld['func']:
                                value = self.func(item_fld['func'], value)
                            doc[item_fld['name']].append(value)
                            count = len(doc[item_fld['name']]) if len(doc[item_fld['name']]) > count else count
        return doc, count

    def document_split_one_line(self, doc:dict, count:int, name:str):
        for i in range(count):
            elem = dict()
            for key, value in doc.items():
                elem[key] = list()
                if i < len(value):
                    elem[key].append(value[i])
                elif len(value) != 0:
                    elem[key].append(value[0])
            self.append_to_collection(name, elem)

    def write_collections(self) -> NoReturn:
        if not self.is_init():
            return False

        path = self._config._parameters['path']
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
        return self.get_value_int(self._config._page_index)

    def get_max_cols(self) -> int:
        return self.get_value_int(self._config._max_cols)

    def get_row_start(self) -> int:
        return self.get_value_int(self._config._row_start)

    def get_max_rows_heading(self) -> int:
        return self.get_value_int(self._config._max_rows_heading)

# ---------- Функции --------------------
    def func(self, key:str, data):
        dic_f = {
            'inn': self.func_inn,
            'hash': self.func_hash,
            'uuid': self.func_uuid,
            'id': self.func_id,
        }
        try:
            f = dic_f[key]
            return f(data)
        except:
            return ''


    def func_inn(self,data):
        return self._parameters['inn'][0]

    def func_hash(self, data):
        return _hashit(data.encode('utf-8'))

    def func_uuid(self, data):
        return uuid.uuid4()

    def func_id(self,data):
        d = self._parameters["period"][0]
        return f'{data}_{d[6:]}_{d[3:5]}'