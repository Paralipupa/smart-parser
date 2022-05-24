import logging
from operator import is_
import re
import os
import hashlib
import datetime
from typing import NoReturn, Union
from itertools import product
import uuid
from .gisconfig import GisConfig, check_error
from .file_readers import get_file_reader

db_logger = logging.getLogger('parser')


def _hashit(s): return hashlib.sha1(s).hexdigest()

class ExcelBaseImporter:

    @check_error
    def __init__(self, file_name: str, config_file: str, inn: str):
        self.is_file_exists = True
        self._team = list()  # список областей с данными
        self.colontitul = {'status': 0, 'is_parameters': False, 'head': list(
        ), 'foot': list()}  # список  записей до и после табличных данных
        self._names = dict()  # колонки таблицы
        self._parameters = dict()  # параметры отчета (период, и др.)
        self._parameters['filename'] = {'fixed': True, 'value': [file_name]}
        self._parameters['inn'] = {'fixed': True, 'value': [inn]}
        self._parameters['config'] = {'fixed': True, 'value': [config_file]}
        self._collections = dict()  # коллекция выходных таблиц
        self._config = GisConfig(config_file)

    @check_error
    def is_verify(self, file_name: str) -> bool:
        if not self.is_init():
            return False
        if not os.path.exists(self._parameters['filename']['value'][0]):
            logging.warning('file not found {}. skip'.format(
                self._parameters['filename']['value'][0]))
            self.is_file_exists = False
            return False
        return True

    @check_error
    def read(self) -> bool:
        if not self.is_verify(self._parameters['filename']['value'][0]):
            return False
        print('Файл {} ({})'.format(
            self._parameters['filename']['value'][0], self._parameters['config']['value'][0]))
        names = None
        row = 0
        if not self._config._header['pattern']:
            self.colontitul['status'] = 1
        data_reader = self.get_data()
        for record in data_reader:
            self.on_read_line(row, record)
            if self.colontitul['status'] != 2:
                if not self.check_bound_row(row):
                    return (len(self._collections) > 0)
                names = self.get_names(record)
                self.check_colontitul(names, row)
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
        for key, value in self._names.items():
            result_record.setdefault(key, [])
            size = len(result_record[key])
            for index in value['indexes']:
                v = record[index]
                is_empty = is_empty and (v == '' or v is None)
                result_record[key].append(
                    {'row': size, 'col': value['col'], 'index': index, 'value': v})
        return result_record if not is_empty else None

    def append_team(self, mapped_record: list) -> bool:
        if not self.get_condition_team():
            match = True
        else:
            match = re.search(self.get_condition_team(),
                              mapped_record[self.get_condition_column()][0]['value'], re.IGNORECASE)
        if match:
            self._team.append(mapped_record)
            return True
        elif len(self._team) != 0:
            for key, value in mapped_record.items():
                size = len(self._team[-1][key])
                self._team[-1][key].append({'row': size,
                                            'col': self._team[-1][key][0]['col'],
                                            'index': self._team[-1][key][0]['index'],
                                            'value': mapped_record[key][0]['value']})
            return False

    def check(self, is_warning: bool = True) -> bool:
        if not self.is_verify(self._parameters['filename']['value'][0]):
            return False
        headers = list()
        rows: list[int] = self._config._check['row']
        cols: list[int] = self._config._check['col']
        pattern: str = self._config._check['pattern']
        index = 0
        data_reader = self.get_data()
        for record in data_reader:
            headers.append(record)
            index += 1
            if index > rows[-1]:
                break
        for row, col in product(rows, cols):
            match = re.search(pattern, headers[row][col], re.IGNORECASE)
            if match:
                return True
        if is_warning:
            logging.warning('файл "{0}" не сооответствует шаблону "{1}". skip'.format(
                self._parameters['filename']['value'][0], self._parameters['config']['value'][0]))
        return False

    def check_bound_row(self, row: int) -> bool:
        if self.get_row_start() + self.get_max_rows_heading() < row:
            s1, s2 = '', ''
            for item in self._config._columns_heading:
                if not item['active']:
                    s1 += item['offset']['pattern']+' '+item['name']+',\n'
                else:
                    s2 += f"{item['offset']['pattern']} {item['name']} ({item['row']},{item['index']}) \n"
            logging.warning('В загружаемом файле "{}" не все колонки найдены \n'.format(
                self._parameters['filename']['value'][0]))
            if s2:
                logging.warning('Найдены колонки:\n {} \n'.format(s2))
            if s1:
                logging.warning('Не найдены колонки:\n {} \n'.format(s1))
            return False
        return True

    def check_colontitul(self, names: list, row: int):
        if self.colontitul['status'] == 0:
            if self.check_headers_status(names):
                if len(self._team) != 0:
                    self.process_record(self._team[-1])
                    self.colontitul['head'] = list()
                    self.colontitul['foot'] = list()
                    self._names = dict()
                    self._team = list()
        if self.check_columns(names, row):
            self._row_start = row
        if self.colontitul['status'] == 1 and (len(self.get_columns_heading()) <= len(self._names)):
            self.colontitul['status'] = 2

    def check_body(self, record: list, row: int):
        mapped_record = self.map_record(record)
        if mapped_record:  # строка не пустая
            # проверяем условие конеца таблицы
            if self.check_end_table(mapped_record):
                self.colontitul['status'] = 0
                self.colontitul['is_parameters'] = False
                self.set_row_start(row)
                for item in self.get_columns_heading():
                    item['active'] = False
                self.colontitul['foot'].append(record)
            elif self.append_team(mapped_record):  # добавили новую область
                if len(self._team) > 1:  # если больше одной области, то добавляем предпоследнюю в документ
                    self.process_record(self._team[-2])
        if len(self._team) < 2:
            self.colontitul['head'].append(record)

    def check_columns(self, names: list, row: int) -> bool:
        is_find = False
        if names:
            # список уже добавленных колонок, которые нужно исключить при следующем прохождении
            cols_exclude = list()
            # сначала проходим колонки без групп
            for item in self.get_columns_heading():
                if not item['group_name']:
                    if self.check_column(item, names, row, cols_exclude):
                        is_find = True
            for item in self.get_columns_heading():
                if item['group_name']:
                    if self.check_column(item, names, row, cols_exclude):
                        is_find = True
        return is_find

    def check_column(self, item: dict, names: list, row: int, cols_exclude: list = []) -> dict:
        is_find = False
        if (not item['active'] or item['group_name']) and item['name']:
            search_names = self.get_search_names(
                names, item['name'], cols_exclude)  # колонки в таблице Excel
            if search_names:
                for name in search_names:
                    b, c = True, item['name']
                    if item['offset']['pattern']:
                        b, c = self.check_column_offset(item, name['col'])
                    if b:
                        self._names.setdefault(c, {'col': item['col'],
                                                   'active': True, 'indexes': []})
                        self._names[c]['active'] = True
                        self._names[c]['indexes'].append(name['col'])
                        cols_exclude.append(name['col'])
                        item['active'] = True
                        item['index'] = name['col']
                        item['row'] = row
                        is_find = True

                        if not item['group_name']:
                            break
        return is_find

    def check_end_table(self, mapped_record) -> bool:
        if not self.get_condition_end_table():
            return False
        match = re.search(self.get_condition_end_table(
        ), mapped_record[self.get_condition_end_table_column()][0]['value'], re.IGNORECASE)
        if match:
            return True
        return False

    def check_period_value(self):
        ls = list()
        for item in self._parameters['period']['value']:
            if item:
                try:
                    month = 0
                    year = 0
                    result = re.search(
                        '(0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[012])[\/\-\.][0-9]{4}',
                        item, re.IGNORECASE)
                    if result:
                        year = item[6:]
                        month = item[3:5]
                    else:
                        result = re.search(
                            '19[89][0-9]|20[0-3][0-9]', item, re.IGNORECASE)
                        if result:
                            year = result.group(0)
                            month = next((val for key, val in self.get_months().items() if re.search(
                                key+'[а-я]+\s', item, re.IGNORECASE)), None)
                    if month:
                        ls.append(f'01.{month}.{year}')
                    else:
                        ls.append(datetime.date.today().strftime('%d.%m.%Y'))
                except:
                    d = datetime.date.today().strftime('%d.%m.%Y')
        self._parameters['period']['value'] = list()
        if ls:
            for item in ls:
                self._parameters['period']['value'].append(item)
        else:
            self._parameters['period']['value'].append(
                datetime.date.today().replace(day=1).strftime('%d.%m.%Y'))

    def check_headers_status(self, names):
        if self.colontitul['status'] == 1:
            return False
        m = self._config._header['pattern']
        if not m:
            self.colontitul['status'] = 1
        else:
            if self.get_search_names(names, m):
                self.colontitul['status'] = 1
        return (self.colontitul['status'] == 1)

    # Проверка на наличие 'якоря' (текста, смещенного относительно позиции текущего заголовка)
    def check_column_offset(self, item: dict, index: int) -> bool:
        dic = item['offset']
        if dic and dic['pattern']:
            rows = [i for i in dic['row']]
            cols = dic['col']
            row_count = len(self.colontitul['head'])
            for row, col in product(rows, cols):
                match = re.search(
                    dic['pattern'], self.colontitul['head'][(row_count-1)+row][index+col], re.IGNORECASE)
                if match:
                    return True, (((item['group_name'] if item['group_name'] else dic['pattern']) +
                                  ' ' + item['name']) if dic['is_include'] else item['name'])
            return False, item['name']
        return True, item['name']

    def get_data(self):
        ReaderClass = get_file_reader(self._parameters['filename']['value'][0])
        data_reader = ReaderClass(self._parameters['filename']['value'][0], self.get_page_name(
        ), 0, range(self.get_max_cols()), self.get_page_index())
        return data_reader

    def get_value_after_validation(self, pattern: str, name: str, row: int, col: int) -> str:
        try:
            match = re.search(
                pattern, self.colontitul[name][row][col], re.IGNORECASE)
            if match:
                return match.group(0).strip()
            else:
                return ''
        except Exception as ex:
            return f'error: {ex}'

    def get_names(self, record) -> dict:
        names = []
        index = 0
        if (self.colontitul['status'] == 1):
            self.colontitul['head'].append(record)
        elif self.colontitul['status'] == 0 and len(self._names) > 0:
            self.colontitul['foot'].append(record)
        for cell in record:
            if cell:
                nm = dict()
                nm['name'] = str(cell).strip()
                nm['col'] = index
                nm['active'] = False
                names.append(nm)
            index += 1
        return names

    def get_search_names(self, names: list, col_name: str, cols_exclude: list = []) -> list:
        results = []
        for name in names:
            if not (name['col'] in cols_exclude) and re.search(f'{col_name}', name['name'], re.IGNORECASE):
                results.append(name)
        return results

    def get_key(self, col: int) -> str:
        for key, value in self._names.items():
            if value['col'] == col:
                return key
        return ''

    def get_value(self, value: str = '', pattern: str = '', type_value: str = '') -> Union[str, int, float]:
        result = re.search(pattern, value.strip(), re.IGNORECASE)
        if not result:
            result = ''
        else:
            result = result.group(0)
        try:
            if type_value == 'int':
                result = int(result.replace(',', '.'))
            elif type_value == 'double' or type_value == 'float':
                result = float(result.replace(',', '.'))
        except:
            result = 0
        return result

    def get_value_str(self, value: str, pattern: str) -> str:
        result = re.search(pattern, value.strip(), re.IGNORECASE)
        if result:
            return result.group(0)
        return ''

    def get_value_int(self, value: list) -> int:
        if value and isinstance(value, list):
            return value[0]
        else:
            return 0

    def get_value_range(self, value: list, count: int = 0) -> list:
        try:
            if value:
                return value
            else:
                return range(count)
        except:
            return range(count)

    def get_months(self) -> dict:
        return {'январ': '01',
                'феврал': '02',
                'март': '03',
                'апрел': '04',
                'май': '05',
                'мая': '05',
                'июн': '06',
                'июл': '07',
                'август': '08',
                'сентябр': '09',
                'октябр': '10',
                'ноябр': '11',
                'декабр': '12'
                }

    def done(self):
        if len(self._team) != 0:
            self.process_record(self._team[-1])

    def on_read_line(self, index, record):
        pass

    def set_parameters(self) -> NoReturn:
        for value in self._parameters.values():
            if not value['fixed']:
                value['value'] = list()
        for key in self._config._parameters.keys():
            self.set_parameter(key)
        self._parameters.setdefault(
            'period', {'fixed': False, 'value': list()})

        if not self._parameters['period']['value']:
            self._parameters['period']['value'].append(
                datetime.date.today().strftime('%d.%m.%Y'))
        self.check_period_value()

        self._parameters.setdefault('path', {'fixed': False, 'value': list()})
        if not self._parameters['path']['value']:
            self._parameters['path']['value'].append('output')
        self._parameters.setdefault(
            'address', {'fixed': False, 'value': list()})
        if not self._parameters['address']['value']:
            self._parameters['address']['value'].append('')
        self.colontitul['is_parameters'] = True

    def set_parameter(self, name: str):
        for param in self._config._parameters[name]:
            rows: list[int] = param['row']
            cols: list[int] = param['col']
            pattern = param['pattern']
            is_head = param['ishead']
            self._parameters.setdefault(
                name, {'fixed': False, 'value': list()})
            if pattern:
                if pattern[0] == '@':
                    self._parameters[name]['value'].append(pattern[1:])
                else:
                    for row, col in product(rows, cols):
                        if is_head:
                            result = self.get_value_after_validation(
                                pattern, 'head', row, col)
                        else:
                            result = self.get_value_after_validation(
                                pattern, 'foot', row, col)
                        if result:
                            self._parameters[name]['value'].append(result)
        return self._parameters[name]

    def process_record(self, team: dict) -> NoReturn:
        if not self.colontitul['is_parameters']:
            self.set_parameters()
        for doc_param in self._config._documents:
            doc = self.set_document(team, doc_param)
            self.document_split_one_line(doc, doc_param)

# ---------- Документы --------------------

    def append_to_collection(self, name: str, doc: dict) -> NoReturn:
        self._collections.setdefault(name, list())
        self._collections[name].append(doc)

# Формирование документа из полученной порции (отдельной области или иерархии)
    def set_document(self, team: dict, doc_param):
        doc = dict()
        for item_fld in doc_param['fields']:  # перебор полей выходной таблицы
            doc.setdefault(item_fld['name'], list())
            # колонки, данные из которых заполняют поле.
            # Каждая колонка создает отдельную запись
            cols = self.get_value_range(item_fld['column'])
            rows_rel = list()
            for col in cols:
                name_field = self.get_key(col)
                if name_field and item_fld['pattern']:
                    rows = self.get_value_range(
                        item_fld['row'], len(team[name_field]))
                    for row in rows:
                        if len(team[name_field]) > row:
                            value = self.get_fld_value(
                                team=team[name_field], type_fld=item_fld['type'],
                                pattern=item_fld['pattern'], row=row)
                            if not value:
                                # если значение пустое, то проверяем под-поля (col_x_y если они заданы)
                                value = self.get_sub_value(
                                    item_fld, team, name_field, row, col)
                            else:
                                if item_fld['row_offset'] or item_fld['column_offset']:
                                    # если есть смещение, то берем данные от туда
                                    value = self.get_value_offset(
                                        team=team, item_fld=item_fld, item_type=item_fld['type'], row=row, col=col)
                                if value and item_fld['func']:
                                    # запускаем функцию и передаем в нее полученное значение
                                    value = self.func(
                                        team=team, fld_param=item_fld, data=value, row=row, col=col)
                            if value:
                                # формируем документ
                                doc[item_fld['name']].append(
                                    {'row': len(doc[item_fld['name']]), 'col': col, 'value': value})
                else:
                    # все равно заносим в документ
                    doc[item_fld['name']].append(
                        {'row': len(doc[item_fld['name']]), 'col': col, 'value': ''})

        return doc

# Разбиваем данные документа по-строчно
    def document_split_one_line(self, doc: dict, doc_param: dict):
        name = doc_param['name']
        # для каждого поля свой индекс прохода
        index = {x: 0 for x in doc.keys()}
        rows = [x[-1]['row'] for x in doc.values() if x]
        counts = [len(x) for x in doc.values() if x]
        rows = rows + counts
        rows_count = max(rows) if rows else 0
        rows_required = self.__get_required_rows(name, doc)
        rows_exclude = [x if x >= 0 else rows_count +
                        1+x for x in doc_param['rows_exclude']]
        i = -1
        done = True

        while done:
            i += 1
            done = (i < rows_count)
            elem = dict()
            is_empty = True
            for key, values in doc.items():
                elem[key] = ""
                if index[key] < len(values):
                    # проверяем соответствие номера строки (row) в данных с номером записи (i) в выходном файле
                    if (values[index[key]]['row'] == i):
                        elem[key] = values[index[key]]['value']
                        is_empty = is_empty and (
                            values[index[key]]['value'] == '')
                        index[key] += 1
                        done = True
                    elif values[0]['row'] == 0:
                        elem[key] = values[0]['value']
                elif len(values) > 0 and values[0]['row'] == 0:
                    elem[key] = values[0]['value']
            if not is_empty and not (i in rows_exclude) and (not rows_required or i in rows_required):
                self.append_to_collection(name, elem)

    def write_collections(self) -> NoReturn:
        if not self.is_init() or len(self._collections) == 0:
            return
        path = self._parameters['path']['value'][0]

        os.makedirs(path, exist_ok=True)

        id = self.func_id()
        for name, records in self._collections.items():
            i = 0
            file_output = f'{path}/{self._parameters["inn"]["value"][0]}{id}_{name}'
            while os.path.exists(f'{file_output}{"("+str(i)+")" if i != 0 else ""}.csv'):
                i+=1
            file_output = f'{file_output}{"("+str(i)+")" if i != 0 else ""}.csv'
            with open(file_output, 'w') as file:
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

    def __get_required_rows(self, name, doc) -> set:
        s = set()
        d = next(
            (x for x in self._config._documents if x['name'] == name), None)
        if d and d['required_fields']:
            for name_field in d['required_fields'].split(','):
                for item in doc[name_field]:
                    s.add(item['row'])
        return s


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

    def set_row_start(self, row: int) -> int:
        self._config._row_start = [row]

    def get_max_rows_heading(self) -> int:
        return self.get_value_int(self._config._max_rows_heading)

    def get_sub_value(self, item_fld, team, name_field, row, col):
        if item_fld['sub']:
            for item_sub in item_fld['sub']:
                value = self.get_fld_value(
                    team=team[name_field], type_fld=item_fld['type'], pattern=item_sub['pattern'], row=row)
                if value:
                    if item_sub['row_offset'] or item_sub['column_offset']:
                        value = self.get_value_offset(
                            team=team, item_fld=item_sub, item_type=item_fld['type'], row=row, col=col)
                    if item_sub['func']:
                        value = self.func(
                            team=team, fld_param=item_sub, data=value, row=row, col=col)
                    return value
        return None

    def get_fld_value(self, team: dict, type_fld: str, pattern: str, row: int) -> str:
        value = self.get_value(type_value=type_fld)
        for val_item in team:
            if val_item['row'] == row:
                value += self.get_value(
                    val_item['value'], pattern, type_fld)
        if (type_fld == 'float' or type_fld == 'double' or type_fld == 'int'):
            if value == 0:
                value = ''
            else:
                value = str(round(value, 4) if isinstance(
                    value, float) else value)
        return value

    def get_value_offset(self, team, item_fld, item_type, row, col):
        # если есть смещение, то берем данные от туда
        value = self.get_value(item_fld['type'])
        rows = list(zip(item_fld['row_offset'], item_fld['row_offset_mark']))
        if not rows:
            # При отсутствии настоек по смещению строки берем значение текущуй строки
            rows = [(0, False)]
        for r in rows:
            col_config = col
            if item_fld['column_offset']:
                col_config = self.get_value_int(item_fld['column_offset'])
            m_key = self.get_key(col_config)
            if m_key:
                value += self.get_fld_value(
                    team=team[m_key], type_fld=item_type, pattern=item_fld['pattern_offset'], row=r[0]+row if not r[1] else r[0])
        return value


# ---------- Функции --------------------

    def func(self, team: dict, fld_param, data: str, row: int, col: int):
        dic_f = {
            'inn': self.func_inn,
            'period': self.func_period,
            'period_last': self.func_period_last,
            'period_month': self.func_period_month,
            'period_year': self.func_period_year,
            'address': self.func_address,
            'column_name': self.func_column_name,
            'column_value': self.func_column_value,
            'hash': self.func_hash,
            'guid': self.func_uuid,
            'param': self.func_param,
            'id': self.func_id,
        }
        pattern = fld_param['func_pattern']
        try:
            for name_func_add in fld_param['func'].split(','):
                value = ''
                for name_func in name_func_add.split('+'):
                    name_func, data_calc, is_check = self.__get_func_name(
                        name_func=name_func, data=data)
                    f = dic_f[name_func.strip()]
                    if is_check:
                        if f(data_calc, row, col, team):
                            value += data_calc + ' '
                    else:
                        value += f(data_calc, row, col, team) + ' '
                data = value.strip()
                if pattern:
                    match = re.search(pattern, data, re.IGNORECASE)
                    pattern = ''  # шаблон проверки применятся только один раз
                    if match:
                        data = match.group(0)
                    else:
                        data = ''
            return data.strip()
        except Exception as ex:
            return f'error {name_func}: {str(ex)}'

    def __get_func_name(self, name_func, data):
        is_check = False
        if name_func.find('(') != -1:
            # если функция с параметром, то заменяем входные данные (data) на этот параметр
            param = re.search(
                r'(?<=\()[a-z_0-9-]+(?=\))', name_func, re.IGNORECASE)
            if param:
                data = param.group(0)
            name_func = name_func[:name_func.find('(')]
        if name_func.find('check_') != -1:
            name_func = name_func.replace('check_', '')
            is_check = True
        return name_func, data, is_check

    def func_inn(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return self._parameters['inn']['value'][0]

    def func_period(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return self._parameters['period']['value'][0]

    def func_period_last(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return self._parameters['period']['value'][-1]

    def func_period_month(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return self._parameters['period']['value'][0][3:5]

    def func_period_year(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return self._parameters['period']['value'][0][6:]

    def func_address(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return self._parameters['address']['value'][0]

    def func_hash(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return _hashit(str(data).encode('utf-8'))

    def func_uuid(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return str(uuid.uuid5(uuid.NAMESPACE_X500, data))

    def func_id(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        d = self._parameters['period']['value'][0]
        return f'{data}_{d[6:]}_{d[3:5]}'

    def func_column_name(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        if col != -1:
            return self._config._columns_heading[col]['group_name'] if self._config._columns_heading[col]['group_name'] else ((self._config._columns_heading[col]['offset']['pattern'] if self._config._columns_heading[col]['offset'] else '') + (self._config._columns_heading[col]['name']))
        return ''

    def func_column_value(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        value = next((x[row]['value']
                     for x in team.values() if x[row]['col'] == int(data)), '')
        return value

    def func_param(self, key: str = '', row: int = -1, col: int = -1, team: dict = {}):
        m = ''
        for item in self._parameters[key]['value']:
            m += (item.strip() + ' ') if isinstance(item, str) else ''
        return f'{m.strip()}'
