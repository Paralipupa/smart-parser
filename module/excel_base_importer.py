import logging
import re, os, hashlib, datetime
from typing import NoReturn
from wsgiref import validate
from module.file_readers import get_file_reader
from module.gisconfig import GisConfig
from itertools import product
import uuid

_hashit = lambda s: hashlib.sha1(s).hexdigest()

# lock = Lock()

class ExcelBaseImporter:

    def __init__(self, file_name:str, inn:str, config_file:str):
        self._team = list()        #список областей с данными
        self._heads_foots = {'status':0, 'is_parameters': False, 'head':list(),'foot':list()}     #список  записей до табличных данных
        self._names = dict()       #заголовки таблиц
        self._parameters = dict()   #параметры отчета (период, и др.)
        self._parameters['filename'] = {'fixed': True, 'value':[file_name]}
        self._parameters['inn'] = {'fixed': True, 'value':[inn]}
        self._parameters['config'] = {'fixed': True, 'value':[config_file]}
        self._collections = dict() #коллекция выходных таблиц
        self._config = GisConfig(config_file)


    def is_verify(self, file_name:str) -> bool:
        if not self.is_init():
            return False
        if not os.path.exists(self._parameters['filename']['value'][0]):
            logging.warning('file not found {}. skip'.format(self._parameters['filename']['value'][0]))
            return False
        return True


    def read(self) -> bool:
        if not self.is_verify(self._parameters['filename']['value'][0]): return False
        print('Файл {} ({})'.format(self._parameters['filename']['value'][0],self._parameters['config']['value'][0]))
        names = None
        row = 0
        if not self.get_condition_end_table():
            self._heads_foots['status'] = 1
        data_reader = self.get_data()
        for record in data_reader:
            self.on_read_line(row,record)
            if self._heads_foots['status'] != 2:
                if not self.check_bound_row(row):
                    return (len(self._collections) > 0)
                names = self.get_names(record)
                self.check_head_and_foot(names, row)
            else:
                self.check_body(record, row)
            row += 1
            if row % 100 == 0:
                print('Обработано: {}   \r'.format(row), end='', flush=True)
        self.done()
        return True


    def map_record(self, record):
        result_record = {}
        is_empty = True
        for key, index in self._names.items():
            v = record[index['index']]
            is_empty = is_empty and (v == '' or v is None)
            result_record[key] = [v]
        return result_record if not is_empty else None


    def append_team(self, mapped_record:list) -> bool:
        if not self.get_condition_team():
            match = True
        else:
            match = re.search(self.get_condition_team(), mapped_record[self.get_condition_column()][0])
        if match:
            self._team.append(mapped_record)
            return True
        elif len(self._team) != 0:
            for key, value in mapped_record.items():
                self._team[-1][key].append(value[0])
            return False


    def check(self, is_warning:bool=True) -> bool:
        if not self.is_verify(self._parameters['filename']['value'][0]): return False
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
            logging.warning('файл "{0}" не сооответствует шаблону "{1}". skip'.format(self._parameters['filename']['value'][0],self._parameters['config']['value'][0]))
        return False


    def check_bound_row(self, row:int) -> bool:
        if self.get_row_start() + self.get_max_rows_heading() < row:
            s1, s2 = '', ''
            for item in self._config._columns_heading:
                if not item['active']:
                    s1 += item['offset']['text']+' '+item['name']+',\n'
                else:
                    s2 += f"{item['offset']['text']} {item['name']} ({item['row']},{item['col']}) \n"
            logging.warning('В загружаемом файле "{}" не все колонки найдены \n'.format(self._parameters['filename']['value'][0]))
            if s2: logging.warning('Найдены колонки:\n {} \n'.format(s2))
            if s1: logging.warning('Не найдены колонки:\n {} \n'.format(s1))
            return False
        return True


    def check_head_and_foot(self, names:list, row:int):
        if self._heads_foots['status'] == 0:
            if self.check_headers_status(names):
                if len(self._team) != 0:
                    self.process_record(self._team[-1])
                self._heads_foots['head'] = list()
                self._heads_foots['foot'] = list()
                self._names  = dict()
                self._team = list()
        if self.check_columns(names, row):
            self._row_start = row
        if self._heads_foots['status'] == 1 and (len(self.get_columns_heading()) <= len(self._names)):
            self._heads_foots['status'] = 2


    def check_body(self, record:list, row:int):
        mapped_record = self.map_record(record)
        if mapped_record and self.append_team(mapped_record):
            if len(self._team) > 1:
                self.process_record(self._team[-2])
        elif len(self._team) == 0:
            self._heads_foots['head'].append(record)
        if mapped_record and self.check_end_table(mapped_record):
            self._heads_foots['status'] = 0
            self._heads_foots['is_parameters'] = False
            self.set_row_start(row)
            for item in self.get_columns_heading():
                item['active'] = False


    def check_columns(self, names:list, row:int) -> bool:
        if names:
            result = dict()
            for item in self.get_columns_heading():
                if not item['active'] and item['name']:
                    index = self.get_index(names, item['name']) #номер колонки в таблице Excel
                    if index != -1:
                        b,c = True, item['name']
                        if item['offset']['text']:
                            b, c = self.check_columns_offset(item, index)
                        if b:
                            result[c] = {'index':index, 'col': item['col'], 'active': False}
                            item['index'] = index
                            item['row'] = row
                            item['active'] = True
            if len(result) > 0:
                self._names.update(result)
                return True
        return False


    def check_end_table(self, mapped_record) ->bool:
        if not self.get_condition_end_table(): return False
        match = re.search(self.get_condition_end_table(), mapped_record[self.get_condition_end_table_column()][0])
        if match:
            return True
        return False


    def check_period_value(self):
        ls=list()
        for item in self._parameters['period']['value']:
            if item:
                try:
                    d = item.strftime('%d.%m.%Y')
                    datetime.date.fromisoformat(    )
                    ls.append(d)
                except:
                    d = datetime.date.today().strftime('%d.%m.%Y')
        self._parameters['period']['value'] = list()
        if ls:
            for item in ls:
                self._parameters['period']['value'].append(item)
        else:
            self._parameters['period']['value'].append(datetime.date.today().strftime('%d.%m.%Y'))


    def check_headers_status(self, names):
        if self._heads_foots['status'] == 1:
            return False
        m = self._config._header['pattern']
        if not m:
            self._heads_foots['status'] = 1
        else:
            col = self.get_index(names, m )
            if col != -1:
                self._heads_foots['status'] = 1
        return (self._heads_foots['status'] == 1)


    # Проверка на наличие 'якоря' (текста, смещенного относительно позиции текущего заголовка)
    def check_columns_offset(self, item:dict, index:int) -> bool:
        dic = item['offset']
        if dic and dic['text']:
            rows = [i for i in dic['row']]
            cols = dic['col']
            row_count = len(self._heads_foots['head'])
            for row, col in product(rows,cols):
                match = re.search(dic['text'],self._heads_foots['head'][(row_count-1)+row][index+col])
                if match:
                    return True, (dic['text'] + ' ' + item['name'] if dic['is_include'] else item['name'])
            return False, item['name']
        return True, item['name']


    def get_data(self):
        ReaderClass = get_file_reader(self._parameters['filename']['value'][0])
        data_reader = ReaderClass(self._parameters['filename']['value'][0], self.get_page_name(), 0, range(self.get_max_cols()), self.get_page_index())
        return data_reader


    def get_re(self, pattern:str, name:str, row:int, col:int):
        try:
            match = re.search(pattern, self._heads_foots[name][row][col])
            if match:
                return match.group(0).strip()
            else:
                return ''
        except:
            return ['error']


    def get_names(self, record) -> dict:
        names = []
        index = 0
        if (self._heads_foots['status'] == 1) or (len(self._collections) == 0):
            self._heads_foots['head'].append(record)
        elif self._heads_foots['status'] == 0:
            self._heads_foots['foot'].append(record)
        for cell in record:
            if cell:
                nm = dict()
                nm['name'] = str(cell).strip()
                nm['col'] = index
                nm['active'] = False
                names.append(nm)
            index += 1
        return names


    def get_index(self, names:list, col_name:str) -> int:
        for name in names:
            if not name['active']:
                match = re.search(f'^{col_name}',name['name'])
                if match:
                    name['active'] = True
                    return name['col']
        return -1


    def get_key(self, col:int) -> str:
        for key, value in self._names.items():
            if value['col'] == col:
                return key
        return ''


    def get_value_str(self, value:str, pattern:str) -> str:
        result = re.search(pattern, value.strip())
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


    def done(self):
        if len(self._team) !=0 :
            self.process_record(self._team[-1])

    def on_read_line(self, index, record):
        pass


    def set_parameters(self) -> NoReturn:
        for value in self._parameters.values():
            if not value['fixed']:
                value['value'] = list()
        for key in self._config._parameters.keys():
            self.set_parameter(key)
        self._parameters.setdefault('period', { 'fixed':False, 'value':list()})

        if not self._parameters['period']['value']:
            self._parameters['period']['value'].append(datetime.date.today().strftime('%d.%m.%Y'))
        # self.check_period_value()

        self._parameters.setdefault('path', { 'fixed':False, 'value':list()})
        if not self._parameters['path']['value']: self._parameters['period']['value'].append('output')
        self._parameters.setdefault('address', { 'fixed':False, 'value':list()})
        if not self._parameters['address']['value']: self._parameters['period']['value'].append('')
        self._heads_foots['is_parameters'] = True


    def set_parameter(self, name:str):
        for param in self._config._parameters[name]:
            rows:list[int] = param['row']
            cols:list[int] = param['col']
            pattern:str = param['pattern']
            is_head:bool = param['ishead']
            self._parameters.setdefault(name, { 'fixed':False, 'value':list()})
            if pattern:
                if pattern[0] == '@':
                    self._parameters[name]['value'].append(pattern[1:])
                else:
                    for row, col in product(rows,cols):
                        if is_head:
                            result = self.get_re(pattern,'head', row, col)
                        else:
                            result = self.get_re(pattern,'foot', row, col)
                        self._parameters[name]['value'].append(result)
        return self._parameters[name]


    def process_record(self, team:dict) -> NoReturn:
        if not self._heads_foots['is_parameters']:
            self.set_parameters()
        for doc_param in self._config._documents:
            doc,count_rows = self.get_document(team, doc_param)
            self.document_split_one_line(doc, count_rows, doc_param['name'])

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
                        if not value:
                            if item_fld['sub']:
                                for item_sub in item_fld['sub']:
                                    value = self.get_value_str(team[key][row], item_sub['pattern'] )
                                    if value:
                                        if item_sub['column_offset']:
                                            m = self.get_key(self.get_value_int(item_sub['column_offset']))
                                            if m:
                                                value = self.get_value_str(team[m][row], item_sub['pattern_offset'] )
                                        if item_sub['func']:
                                            value = self.func(item_sub['func'], item_sub['func_pattern'], value)
                                        break
                        else:
                            if item_fld['column_offset']:
                                m = self.get_key(self.get_value_int(item_fld['column_offset']))
                                if m:
                                    value = self.get_value_str(team[m][row], item_fld['pattern_offset'] )
                            if item_fld['func']:
                                value = self.func(item_fld['func'], item_fld['func_pattern'], value)
                        if value:
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
                        #проверяем соответствие номера строки в данных с номером записи в выходном файде
                        index = next((x['index'] for x in count_rows['rel'] if x['row']==value[i]['row']), 0)
                        if i >= index:
                            elem[key] = value[i]['value']
                    elif len(value) != 0:
                        elem[key] = value[0]['value']
            self.append_to_collection(name, elem)


    def write_collections(self) -> NoReturn:
        if not self.is_init() or len(self._collections) == 0:
            return

        path = self._parameters['path']['value'][0]
        os.makedirs(path,exist_ok=True)
        for name, records in self._collections.items():
            with open(f'{path}/{name}.csv', 'w') as file:
                file.write(f'{{')
                for key, value in self._parameters.items():
                    file.write(f'\t{key}:"')
                    for val in value["value"]:
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


    def get_condition_team(self) -> str:
        return self._config._condition_team


    def get_condition_end_table(self) -> str:
        return self._config._condition_end_table


    def get_condition_column(self) -> str:
        return self._config._condition_team_column


    def get_condition_end_table_column(self) -> str:
        return self._config._condition_end_table_column


    def get_page_name(self) -> str:
        return self._config._page_name


    def get_page_index(self) -> int:
        return self.get_value_int(self._config._page_index)


    def get_max_cols(self) -> int:
        return self.get_value_int(self._config._max_cols)


    def get_row_start(self) -> int:
        return self.get_value_int(self._config._row_start)


    def set_row_start(self, row:int) -> int:
        self._config._row_start = [row]


    def get_max_rows_heading(self) -> int:
        return self.get_value_int(self._config._max_rows_heading)

# ---------- Функции --------------------
    def func(self, keys:str, pattern:str, data:str):
        dic_f = {
            'inn': self.func_inn,
            'period': self.func_period,
            'period_last': self.func_period_last,
            'period_month': self.func_period_month,
            'period_year': self.func_period_year,
            'address': self.func_address,
            'hash': self.func_hash,
            'guid': self.func_uuid,
            'param': self.func_param,
            'id': self.func_id,
        }
        try:
            for key in keys.split(','):
                if key.find('(') != -1:
                    param = re.search(r'(?<=\()[a-z_0-9-]+(?=\))',key)
                    if param:
                        data = param.group(0)
                    key = key[:key.find('(')]
                f = dic_f[key]
                data = f(data)
                if pattern:
                    match = re.search(pattern,data.strip())
                    if match:
                        data = match.group(0)
            return data
        except:
            return ''


    def func_inn(self,data:str=''):
        return self._parameters['inn']['value'][0]


    def func_period(self,data:str=''):
        return self._parameters['period']['value'][0]


    def func_period_last(self,data:str=''):
        return self._parameters['period']['value'][-1]


    def func_period_month(self,data:str=''):
        return self._parameters['period']['value'][-1]


    def func_period_year(self,data:str=''):
        return self._parameters['period']['value'][-1]


    def func_address(self,data:str=''):
        return self._parameters['address']['value'][0]


    def func_hash(self, data:str=''):
        return _hashit(data.encode('utf-8'))


    def func_uuid(self, data:str=''):
        return uuid.uuid5(uuid.NAMESPACE_X500, data)


    def func_id(self,data:str=''):
        d = self._parameters['period']['value'][0]
        return f'{data}_{d[6:]}_{d[3:5]}'


    def func_param(self, key:str):
        m:str= ''
        for item in self._parameters[key]['value']:
            m += item.strip() + ' '
        return f'{m.strip()}'