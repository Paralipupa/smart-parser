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

    def is_verify(self, file_name:str) -> bool:
        if not self.is_init():
            return False
        if not os.path.exists(self._parameters['filename'][0]):
            logging.warning('file not found {}. skip'.format(self._parameters['filename'][0]))
            return False
        return True

    def get_data(self):
        ReaderClass = get_file_reader(self._parameters['filename'][0])
        data_reader = ReaderClass(self._parameters['filename'][0], self.get_page_name(), 0, range(self.get_max_cols()), self.get_page_index())
        return data_reader

    def check(self, is_warning:bool=True) -> bool:
        if not self.is_verify(self._parameters['filename'][0]): return False
        headers = list()
        rows:list[int] = self._config._check['row']
        cols:list[int] = self._config._check['col']
        pattern:str = self._config._check['pattern']
        index = 0
        data_reader = self.get_data()
        for record in data_reader:
            headers.append(record)
            index +=1
            if index > rows[-1]:
                break
        for row, col in product(rows,cols):
            match = re.search(pattern, headers[row][col])
            if match:
                return True
        if is_warning:
            logging.warning('файл "{0}" не сооответствует шаблону "{1}". skip'.format(self._parameters['filename'][0],self._parameters['config'][0]))
        return False



    def read(self) -> bool:
        if not self.is_verify(self._parameters['filename'][0]): return False
        print('Файл {} ({})'.format(self._parameters['filename'][0],self._parameters['config'][0]))
        is_header = True
        names = None
        row = 0
        data_reader = self.get_data()
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
            else:
                mapped_record = self.map_record(record)
                if mapped_record and self.append_team(mapped_record):
                    if len(self._team) > 1:
                        self.process_record(self._team[-2])
                    else:
                        self.set_parameters()
                elif len(self._team) == 0:
                    self._headers.append(record)
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
        if match:
            self._team.append(mapped_record)
            return True
        elif len(self._team) != 0:
            for key, value in mapped_record.items():
                self._team[-1][key].append(value[0])
            return False

    def set_parameters(self) -> NoReturn:
        if not self.set_fixed_parameters('period'):
            self._parameters['period'].append(datetime.date.today())
        if not self.set_fixed_parameters('address'):
            self._parameters['period'].append('')

    def set_fixed_parameters(self, name:str):
        rows:list[int] = self._config._parameters[name]['row']
        cols:list[int] = self._config._parameters[name]['col']
        pattern:str = self._config._parameters[name]['pattern']
        self._parameters.setdefault(name,list())
        if pattern:
            if pattern[0] == '@':
                self._parameters[name].append(pattern[1:])
            else:
                for row, col in product(rows,cols):
                    result = re.findall(pattern, self._headers[row][col])
                    for item in result:
                        self._parameters[name].append(item)
        return self._parameters[name]


    def process_record(self, team:dict) -> NoReturn:
        for doc_param in self._config._documents:
            doc,count_rows = self.get_document(team, doc_param)
            self.document_split_one_line(doc, count_rows, doc_param['name'])

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
        count_rows = {'count': 0, 'rel' : list()}
        for item_fld  in doc_param['fields']:
            doc.setdefault(item_fld['name'], list())
            key = self.get_key(self.get_value_int(item_fld['column']))
            if key and item_fld['pattern']:
                rows = self.get_value_range(item_fld['row'], len(team[key]))
                rows_rel = list()
                for row in rows:
                    if len(team[key]) > row and team[key][row]:
                        value = self.get_value_str(team[key][row], item_fld['pattern'] )
                        if value:
                            if item_fld['column_offset']:
                                key = self.get_key(self.get_value_int(item_fld['column_offset']))
                                if key:
                                    value = self.get_value_str(team[key][row], item_fld['pattern_offset'] )
                            if item_fld['func']:
                                value = self.func(item_fld['func'], value)
                            rows_rel.append({'index':len(doc[item_fld['name']]), 'row':row})    
                            doc[item_fld['name']].append({'row':row, 'value':value})
                            if len(doc[item_fld['name']]) > count_rows['count']:
                                count_rows['count'] = len(doc[item_fld['name']]) 
                                count_rows['rel'] = rows_rel

        return doc, count_rows

    def document_split_one_line(self, doc:dict, count_rows:dict, name:str):
        for i in range(count_rows['count']):
            elem = dict()
            for key, value in doc.items():
                elem[key] = ""
                if value:
                    if i < len(value):
                        index = next((x['index'] for x in count_rows['rel'] if x['row']==value[i]['row']), 0)
                        if i >= index:
                            elem[key] = value[i]['value']
                    elif len(value) != 0: 
                        elem[key] = value[0]['value']
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
                    file.write(f'\t{key}:"')
                    for val in value:
                        file.write(f'{val} ')
                    file.write(f'",\n')
                file.write(f'}},\n')

                for rec in records:
                    file.write(f'{{\n')
                    for fld_name, val in rec.items():
                        file.write(f'\t{fld_name}:"')
                        file.write(f'{val}')
                        file.write(f'",\n')
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
    def func(self, keys:str, data):
        dic_f = {
            'inn': self.func_inn,
            'period': self.func_period,
            'period_last': self.func_period_last,
            'address': self.func_address,
            'hash': self.func_hash,
            'guid': self.func_uuid,
            'id': self.func_id,
        }
        try:
            for key in keys.split(','):
                f = dic_f[key]
                data = f(data)
            return data
        except:
            return ''


    def func_inn(self,data:str=''):
        return self._parameters['inn'][0]

    def func_period(self,data:str=''):
        return self._parameters["period"][0]

    def func_period_last(self,data:str=''):
        return self._parameters["period"][-1]

    def func_address(self,data:str=''):
        return self._parameters["address"][0]

    def func_hash(self, data:str=''):
        return _hashit(data.encode('utf-8'))

    def func_uuid(self, data:str=''):
        return uuid.uuid5(uuid.NAMESPACE_X500, data)

    def func_id(self,data:str=''):
        d = self._parameters["period"][0]
        return f'{data}_{d[6:]}_{d[3:5]}'