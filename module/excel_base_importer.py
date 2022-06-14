import logging
import re
import os
import hashlib
import datetime
import pathlib
import uuid
import csv
import json
from operator import is_
from ast import Return
from asyncio.log import logger
from typing import NoReturn, Union
from itertools import product
from .gisconfig import GisConfig, fatal_error, warning_error, regular_calc, PATH_LOG, PATH_OUTPUT
from .file_readers import get_file_reader

db_logger = logging.getLogger('parser')
def _hashit(s): return hashlib.sha1(s).hexdigest()


class ExcelBaseImporter:

    @fatal_error
    def __init__(self, file_name: str, config_file: str, inn: str, data: list = None):
        self.is_file_exists = True
        self._teams = list()  # список областей с данными
        self._page_index = 0
        self._page_name = ''
        self._headers = data
        self.colontitul = {'status': 0, 'is_parameters': False, 'head': list(
        ), 'foot': list()}  # список  записей до и после табличных данных
        self._names = dict()  # колонки таблицы
        self._parameters = dict()  # параметры отчета (период, и др.)
        self._parameters['filename'] = {'fixed': True, 'value': [file_name]}
        self._parameters['inn'] = {'fixed': True, 'value': [inn]}
        self._parameters['config'] = {'fixed': True, 'value': [config_file]}
        self._collections = dict()  # коллекция выходных таблиц
        self._config = GisConfig(config_file)

    @fatal_error
    def is_verify(self, file_name: str) -> bool:
        if not self.is_init():
            return False
        if not os.path.exists(self._parameters['filename']['value'][0]):
            self._config._warning.append(
                f"ОШИБКА чтения файла {self._parameters['filename']['value'][0]}")
            self.is_file_exists = False
            return False
        return True

    @fatal_error
    def read(self) -> bool:
        if not self.is_verify(self._parameters['filename']['value'][0]):
            return False
        print('Файл {} ({})'.format(
            self._parameters['filename']['value'][0], self._parameters['config']['value'][0]))
        if not self.get_col_start():
            self.set_col_start(0)
        for col_start in self.get_col_start():
            self.init_data()
            self._col_start = col_start[0]
            pages = list()
            page_indexes = self.get_page_index()
            page_names = self.get_page_name().split(',')
            if page_names:
                pages = [(x, False) for x in page_names]
            else:
                pages += page_indexes
            for page in pages:
                self._page_name = page[0] if not page[1] else ''
                self._page_index = page[0] if page[1] else 0
                names = None
                row = 0
                if not self.get_header('pattern'):
                    self.colontitul['status'] = 1
                data_reader = self._get_data_xls()
                if not data_reader:
                    self._config._warning.append(
                        f"\nОШИБКА чтения файла {self._parameters['filename']['value'][0]}")
                    continue
                for record in data_reader:
                    record = record[self._col_start:]
                    self.on_read_line(row, record)
                    if self.colontitul['status'] != 2:
                        # Область до или после таблицы
                        if not self.check_bound_row(row):
                            # return (len(self._collections) > 0)
                            break
                        names = self._get_names(record)
                        self.check_colontitul(names, row, record)
                    if self.colontitul['status'] == 2:
                        # Табличная область данных
                        self.check_body(record, row)
                    row += 1
                    if row % 100 == 0:
                        print('Обработано: {}   \r'.format(
                            row), end='', flush=True)
                self.done()
                self._page_index += 1
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
        if self.check_condition_team(mapped_record):
            self._teams.append(mapped_record)
            return True
        elif len(self._teams) != 0:
            for key in mapped_record.keys():
                size = len(self._teams[-1][key])
                self._teams[-1][key].append({'row': size,
                                            'col': self._teams[-1][key][0]['col'],
                                             'index': self._teams[-1][key][0]['index'],
                                             'value': mapped_record[key][0]['value']})
        return False

    def check(self, is_warning: bool = False) -> bool:
        if not self.is_verify(self._parameters['filename']['value'][0]):
            return False
        patts = self._get_check_pattern()
        self._headers = self._get_headers()
        if not self._headers:
            return False
        return self._check_controll(self._headers, patts, is_warning)

    def check_condition_team(self, mapped_record: list) -> bool:
        if not self.get_condition_team():
            return True
        if not mapped_record:
            return False
        b = False
        for patt in self.get_condition_team():
            result = regular_calc(
                patt, mapped_record[self.get_condition_column()][0]['value'])
            b = False if not result or result.find('error') != -1 else True
            if b:
                if len(self._teams) != 0:
                    # Проверяем значение со значением из предыдущей области (иерархии)
                    # если не совпадает, то фиксируем начало новой области (иерархии)
                    pred = regular_calc(
                        patt, self._teams[-1][self.get_condition_column()][0]['value'])
                    b = (result != pred)
                if b:
                    break
        return b

    def check_bound_row(self, row: int) -> bool:
        if self.get_row_start() + self.get_max_rows_heading() < row:
            if len(self._teams) != 0:
                return False
            s1, s2, is_active_find = '', '', False
            for item in self.get_columns_heading():
                if not item['active']:
                    if not item['optional']:
                        s1 += f"{item['name']} {'не обязат.' if item['optional'] else ''},\n"
                        is_active_find = True
                else:
                    c = ''
                    for i in item['indexes']:
                        c += f"({item['row']},{i}) "
                    s2 += f"{item['name']} {c}\n"

            if is_active_find:
                self._config._warning.append('\n{}:\nВ загружаемом файле "{}"\nне все колонки найдены \n'.format(
                    self._config._config_name,
                    self._parameters['filename']['value'][0]))
                if s2:
                    self._config._warning.append(
                        'Найдены колонки:\n{}\n'.format(s2.strip()))
                if s1:
                    self._config._warning.append(
                        'Не найдены колонки:\n{}\n'.format(s1.strip()))
            else:
                s = 'Найдены колонки:'
                for key, value in self._names.items():
                    s += f"\n{key} - {value['indexes'][0]}"
                self._config._warning.append('\n{0}:\nВ загружаемом файле "{1}" \
                \nне верен шаблон нахождения начала области данных(({3})condition_begin_team({2}))\n{4}\n'
                                             .format(
                                                 self._config._config_name,
                                                 self._parameters['filename']['value'][0],
                                                 self.get_condition_team(),
                                                 self.get_condition_column(),
                                                 s
                                             ))

            return False
        return True

    def check_colontitul(self, names: list, row: int, record: list):
        if self.colontitul['status'] == 0:
            if self.check_headers_status(names):
                if len(self._teams) != 0:
                    self.process_record(self._teams[-1])
                    self.init_data()
                    self.set_row_start(row)
        if self.check_columns(names, row):
            self._row_start = row
        if self.colontitul['status'] == 1:
            if self.check_stable_columns():
                if (len(self.get_columns_heading()) <= len(self._names)) or \
                        self.check_condition_team(self.map_record(record)):
                    # переход в табличную область данных
                    self.colontitul['status'] = 2
                    self._config._parameters.setdefault(
                        'table_start',
                        [{'row': [row], 'col': [0],
                          'pattern':[f"@{row}"], 'ishead':True}
                         ]
                    )

    def check_body(self, record: list, row: int):

        if self._config._rows_exclude:
            if row in [x[0]+self._config._parameters['table_start'][0]['row'][0] for x in self._config._rows_exclude]:
                if self.colontitul['head'] and self.colontitul['head'][-1] != record:
                    self.colontitul['head'].append(record)
                return
        mapped_record = self.map_record(record)
        if mapped_record:  # строка не пустая
            # проверяем условие конца таблицы
            if self.check_end_table(mapped_record):
                self.colontitul['status'] = 0
                self.colontitul['is_parameters'] = False
                self.set_row_start(row)
                for item in self.get_columns_heading():
                    item['active'] = False
                self.colontitul['foot'].append(record)
            elif self.append_team(mapped_record):  # добавляем новую область
                # если уже нашли более одной области, то добавляем предпоследнюю в документ
                if len(self._teams) > 1:
                    self.process_record(self._teams[-2])
        if len(self._teams) < 2:
            self.colontitul['head'].append(record)

    def check_columns(self, names: list, row: int) -> bool:
        is_find = False
        if names:
            # список уже добавленных колонок, которые нужно исключить при следующем прохождении
            cols_exclude = list()
            for x in [x['indexes'] for x in self._names.values()]:
                cols_exclude.extend(x)
            # сначала проверяем обязательные колонки
            for item in self.get_columns_heading():
                if (not item['active'] or item['duplicate']) and not item['optional'] and item['pattern'][0]:
                    if self.check_column(item, names, row, cols_exclude):
                        is_find = True
            # потом проверяем не обязательные колонки
            for item in self.get_columns_heading():
                if (not item['active'] or item['duplicate']) and item['optional'] and item['pattern'][0]:
                    b = not item['after_stable']
                    if not b and self.check_stable_columns() and (row in self._get_rows_header() or item['duplicate']):
                        b = True
                    if b and self.check_column(item, names, row, cols_exclude):
                        is_find = True
        return is_find

    def check_column(self, item: dict, names: list, row: int, cols_exclude: list = []) -> dict:
        is_find = False
        for p in item['pattern']:
            search_names = self._get_search_names(
                names, p, cols_exclude if not item['duplicate'] else [])  # колонки в таблице Excel
            if search_names:
                break
        if search_names:
            for search_name in search_names:
                b = True
                if item['offset']['pattern'][0]:
                    b = self.check_column_offset(item, search_name['col'])
                if b:
                    col_left = self._get_border(item, 'left', 0)
                    col_right = self._get_border(
                        item, 'right', search_name['col'])
                    if col_left <= search_name['col'] <= col_right:
                        key = item['name']
                        self._names.setdefault(key, {'row': row,
                                                     'col': item['col'],
                                                     'active': True,
                                                     'indexes': []})
                        self._names[key]['active'] = True
                        item['active'] = True
                        if item['col_data']:
                            for ind in item['col_data']:
                                index = ind[0] + \
                                    search_name['col'] if not ind[1] else 0
                                item['indexes'].append(index)
                                self._names[key]['indexes'].append(index)
                        else:
                            item['indexes'].append(search_name['col'])
                            self._names[key]['indexes'].append(
                                search_name['col'])
                        item['row'] = row
                        is_find = True
                        cols_exclude.append(search_name['col'])
                        if item['unique']:
                            break
        return is_find

    # Проверка на наличие всех обязательных колонок
    def check_stable_columns(self) -> bool:
        return all([x['active'] for x in self.get_columns_heading() if not x['optional']])

    # Проверка на наличие 'якоря' (текста, смещенного относительно позиции текущего заголовка)
    def check_column_offset(self, item: dict, index: int) -> bool:
        offset = item['offset']
        if offset and offset['pattern'][0]:
            rows = [i for i in offset['row']]
            if not rows:
                rows = [(0, False)]
            cols = offset['col']
            if not cols:
                cols = [(i, True)
                        for i in range(len(self.colontitul['head'][-1]))]
            row_count = len(self.colontitul['head'])
            col_left = self._get_border(item, 'left', 0)
            col_right = self._get_border(item, 'right', index)
            if col_left <= index <= col_right:
                for row, col in product(rows, cols):
                    r = row[0] if row[1] else (row_count-1)+row[0]
                    c = col[0] if col[1] else index+col[0]
                    if not (r == 0 and c == 0) and 0 <= r < len(self.colontitul['head']) \
                            and 0 <= c < len(self.colontitul['head'][r]):
                        result = regular_calc(
                            offset['pattern'][0], self.colontitul['head'][r][c])
                        if result and result.find('error') == -1:
                            return True
            return False
        return True

    def check_end_table(self, mapped_record) -> bool:
        if not self.get_condition_end_table():
            return False
        result = regular_calc(self.get_condition_end_table(
        ), mapped_record[self.get_condition_end_table_column()][0]['value'])
        if result and result.find('error') == -1:
            return True
        return False

    def check_period_value(self):
        patts = ['%d-%m-%Y', '%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d',
                 '%d-%m-%y', '%d.%m.%y', '%d/%m/%y', '%B %Y']
        d = None
        for item in self._parameters['period']['value']:
            if item:
                for p in patts:
                    try:
                        d = datetime.datetime.strptime(item, p)
                        break
                    except:
                        pass
        ls = list()
        if d:
            ls.append(d.date().replace(day=1).strftime('%d.%m.%Y'))
            ls.append(d.date().strftime('%d.%m.%Y'))
        else:
            result = regular_calc('19[89][0-9]|20[0-3][0-9]', item)
            if result and result.find('error') == -1:
                year = result
                month = next((val for key, val in self._get_months().items() if re.search(
                    key+'[а-я]+\s', item, re.IGNORECASE)), None)
                if month:
                    ls.append(f'01.{month}.{year}')
                else:
                    ls.append(datetime.date.today().strftime('%d.%m.%Y'))
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
        m = self.get_header('pattern')
        if not m:
            self.colontitul['status'] = 1
        else:
            if self._get_search_names(names, m):
                self.colontitul['status'] = 1
        return (self.colontitul['status'] == 1)

    @warning_error
    def _get_data_xls(self):
        ReaderClass = get_file_reader(self._parameters['filename']['value'][0])
        data_reader = ReaderClass(self._parameters['filename']['value'][0], self._page_name, 0,
                                  range(self._col_start + self.get_max_cols()), self._page_index)
        if not data_reader:
            self.is_file_exists = False
            self._config._warning.append(
                f"\nОШИБКА чтения файла {self._parameters['filename']['value'][0]}")
            return None
        return data_reader

    def _get_border(self, item, name: str, col: int = 0) -> int:
        if item[name]:
            name_field = self._get_key(item[name][0][0])
            if name_field:
                col = self._names[name_field]['indexes'][0]
        return col

    def _get_rows_header(self) -> set:
        return {x['row'] for x in self._names.values()}

    def _get_check_pattern(self) -> list:
        rows: list[int] = self.get_check('row')
        if not rows:
            rows.append((0, False))
        patts = list()
        p = self.get_check('pattern')
        patts.append({'pattern': p, 'full': True,
                     'find': p == '', 'maxrow': rows[-1][0]})
        i = 0
        p = self.get_check(f'pattern_{i}')
        while p:
            p = self.get_check(f'pattern_{i}')
            patts.append({'pattern': p, 'full': True,
                         'find': False, 'maxrow': rows[-1][0]})
            i += 1
            p = self.get_check(f'pattern_{i}')

        for item in self._config._columns_heading:
            s = ''
            for patt in item['pattern']:
                s += patt + '|'
            s = s.strip('|')
            patts.append(
                {'pattern': s, 'full': False, 'find': item['optional'] or not s,
                 'maxrow': self._config._max_rows_heading[0][0]})
        return patts

    def _get_headers(self) -> list:
        if self._headers:
            return self._headers
        else:
            self._col_start = 0
            data_reader = self._get_data_xls()
            if not data_reader:
                return None
            headers = list()
            index = 0
            for record in data_reader:
                headers.append(record)
                index += 1
                if index > self._config._max_rows_heading[0][0]:
                    break
        return headers

    def _check_controll(self, headers: list, patts: list, is_warning: bool = False) -> list:
        for row in range(self._config._max_rows_heading[0][0]):
            if row < len(headers):
                for pattern in patts:
                    if pattern['maxrow'] > row and pattern['pattern']:
                        if pattern['full']:
                            s = (' '.join(headers[row])).strip()
                            if s:
                                result = regular_calc(pattern['pattern'], s)
                                if result and result.find('error') == -1:
                                    pattern['find'] = True
                        else:
                            for s in headers[row]:
                                if s:
                                    result = regular_calc(
                                        pattern['pattern'], s)
                                    if result and result.find('error') == -1:
                                        pattern['find'] = True
        i = 0
        s = ''
        for pattern in patts:
            if not pattern['find']:
                s += f"\t{pattern['pattern']}\n"
                i += 1
        if i == 0:
            return self._check_function()
        if (100 - round(i/len(patts) * 100, 0)) > 95:
            self._config._warning.append('\nфайл "{0}"\nсооответствует шаблону "{1}"\nболее, чем на 95%\nНе найдены:\n{2}'.format(
                self._parameters['filename']['value'][0], self._parameters['config']['value'][0], s))
        if is_warning:
            self._config._warning.append('файл "{0}" не сооответствует шаблону "{1}". skip'.format(
                self._parameters['filename']['value'][0], self._parameters['config']['value'][0]))
        return False

    def _check_function(self) -> bool:
        f = self._config._check['func']
        if not f:
            return True
        patt = [self._config._check['func_pattern']]
        item_fld = {'func': f, 'func_pattern': patt,
                    'type': '', 'offset_type': ''}
        value = self.func(
            team=dict(), fld_param=item_fld, data='', row=0, col=0)
        return True if value else False

    def _get_value_after_validation(self, pattern: str, name: str, row: int, col: int) -> str:
        try:
            if row < len(self.colontitul[name]) and col < len(self.colontitul[name][row]) \
                    and self.colontitul[name][row][col]:
                result = regular_calc(pattern, self.colontitul[name][row][col])
                if result:
                    return result
                else:
                    return ''
            else:
                return ''
        except Exception as ex:
            return f'error: {ex}'

    def _get_names(self, record) -> dict:
        names = []
        index = 0
        if (self.colontitul['status'] == 1) or (self.colontitul['status'] == 0 and len(self._names) == 0):
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

    def _get_search_names(self, names: list, pattern: str, cols_exclude: list = []) -> list:
        results = []
        for name in names:
            if not (name['col'] in cols_exclude):
                result = regular_calc(f'{pattern}', name['name'])
                if result and result.find('error') == -1:
                    results.append(name)
        return results

    def _get_key(self, col: int) -> str:
        for key, value in self._names.items():
            if value['col'] == col:
                return key
        return ''

    def _get_value(self, value: str = '', pattern: str = '', type_value: str = '') -> Union[str, int, float]:
        try:
            value = str(value)
            if type_value == 'int':
                value = str(int(value.replace(',', '.').replace(' ', '')))
            elif type_value == 'double' or type_value == 'float':
                value = str(
                    round(float(value.replace(',', '.').replace(' ', '')), 2))
        except:
            pass
        result = regular_calc(pattern, value)
        try:
            if type_value == 'int':
                result = int(result.replace(',', '.').replace(' ', ''))
            elif type_value == 'double' or type_value == 'float':
                result = round(
                    float(result.replace(',', '.').replace(' ', '')), 2)
        except:
            result = 0
        return result

    def _get_value_str(self, value: str, pattern: str) -> str:
        return regular_calc(pattern, value)

    def _get_value_int(self, value: list) -> int:
        try:
            if value:
                if isinstance(value, list):
                    return value[0]
                elif isinstance(value, str):
                    return int(value)
            else:
                return 0
        except:
            return 0

    def _get_float(self, value: str) -> int:
        try:
            if value:
                if isinstance(value, str):
                    return float(value.replace(',', '.').replace(' ', ''))
                else:
                    return 0
            else:
                return 0
        except:
            return 0

    def _get_value_range(self, value: list, count: int = 0) -> list:
        try:
            if value:
                return value
            else:
                return [(i, True) for i in range(count)]
        except:
            return [(i, True) for i in range(count)]

    def _get_months(self) -> dict:
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

    def _get_doc_param_fld(self, name: str, fld_name: str):
        doc = next((x for x in self.get_config_documents()
                   if x['name'] == name), None)
        if doc:
            fld = next((x for x in doc['fields']
                       if x['name'] == fld_name), None)
            return fld
        return None

    def _get_data_records(self, item_fld):
        records = list()
        records.append(item_fld.copy())
        records[-1]['value'] = 0 if records[-1]['type'] == 'float' or records[-1]['type'] == 'int' else ''
        records[-1]['value_o'] = 0 if (
            records[-1]['offset_type'] == 'float' or records[-1]['offset_type'] == 'int') else ''
        for sub in item_fld['sub']:
            records.append(sub.copy())
            records[-1]['value'] = 0 if records[-1]['type'] == 'float' or records[-1]['type'] == 'int' else ''
            records[-1]['value_o'] = 0 if (
                records[-1]['offset_type'] == 'float' or records[-1]['offset_type'] == 'int') else ''
        return records

    def _get_fld_value(self, team: dict, type_fld: str, pattern: str, row: int) -> str:
        value = self._get_value(type_value=type_fld)
        for val_item in team:
            if val_item['row'] == row:
                value += self._get_value(
                    val_item['value'], pattern, type_fld)
        if (type_fld == 'float' or type_fld == 'double' or type_fld == 'int'):
            if value == 0:
                value = 0
            else:
                value = round(value, 2) if isinstance(
                    value, float) else value
        return value

    # если есть смещение, то берем данные от туда
    def _get_value_offset(self, team, record, row_curr, col_curr):
        rows = record['offset_row']
        cols = record['offset_column']
        value = record['value_o']
        if not rows:
            rows = [(0, False)]
        if not cols:
            cols = [(col_curr, True)]
        fld_name = self._get_key(cols[0][0])
        if fld_name:
            value += self._get_fld_value(
                team=team[fld_name],
                type_fld=record['offset_type'],
                pattern=record['offset_pattern'][0],
                row=rows[0][0]+row_curr if not rows[0][1] else rows[0][0]
            )
        return value

    def _get_required_rows(self, name, doc) -> set:
        s = set()
        d = next(
            (x for x in self.get_config_documents() if x['name'] == name), None)
        if d and d['required_fields']:
            for name_field in d['required_fields'].split(','):
                fld_type = next((x['type']+x['offset_type']
                                for x in d['fields'] if x['name'] == name_field), '')
                for item in doc[name_field]:
                    val = self._get_value(str(item['value']), '.+', fld_type)
                    if val:
                        s.add(item['row'])
        return s

    def _is_data_depends(self, record, doc, doc_param):
        if not record['depends']:
            return True
        fld = record['depends']
        if doc[fld] and doc[fld][0]['value']:
            fld_param = self._get_doc_param_fld(
                doc_param['name'], fld)
            x = self._get_value(
                doc[fld][0]['value'], '.+', fld_param['type'] + fld_param['offset_type'])
        else:
            x = ''
        return x

    def done(self):
        if len(self._teams) != 0:
            self.process_record(self._teams[-1])

    def on_read_line(self, index, record):
        pass

    def _set_parameters(self) -> NoReturn:
        for value in self._parameters.values():
            if not value['fixed']:
                value['value'] = list()
        for key in self.get_config_parameters().keys():
            self._set_parameter(key)
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

    def _set_parameter(self, name: str):
        for param in self.get_config_parameters(name):
            rows = param['row']
            cols = param['col']
            patterns = param['pattern']
            is_head = param['ishead']
            self._parameters.setdefault(
                name, {'fixed': False, 'value': list()})
            for pattern in patterns:
                if pattern:
                    if pattern[0] == '@':
                        self._parameters[name]['value'].append(pattern[1:])
                    else:
                        for row, col in product(rows, cols):
                            result = self._get_value_after_validation(
                                pattern, 'head' if is_head else 'foot', row[0], col[0])
                            if result:
                                if param['offset_pattern']:
                                    if not param['offset_row']:
                                        param['offset_row'].append((0, False))
                                    if not param['offset_col']:
                                        param['offset_col'].append((0, False))
                                    result = self._get_value_after_validation(param['offset_pattern'],
                                            'head' if is_head else 'foot',
                                            param['offset_row'][0][0] + row[0] if not param['offset_row'][0][1] else param['offset_row'][0][0],
                                            param['offset_col'][0][0] + col[0] if not param['offset_col'][0][1] else param['offset_col'][0][0])
                                if result:
                                    self._parameters[name]['value'].append(result)
                                    break

        return self._parameters[name]

    def process_record(self, team: dict) -> NoReturn:
        if not self.colontitul['is_parameters']:
            self._set_parameters()
        for doc_param in self.get_config_documents():
            doc = self.set_document(team, doc_param)
            self.document_split_one_line(doc, doc_param)
        self._teams.remove(team)

# ---------- Документы --------------------
    def append_to_collection(self, name: str, doc: dict) -> NoReturn:
        key = self._page_name if self._page_name else 'noname'
        self._collections.setdefault(name, {key: list()})
        self._collections[name].setdefault(key, list())
        self._collections[name][key].append(doc)

# Формирование документа из полученной порции (отдельной области или иерархии)
    def set_document(self, team: dict, doc_param):
        doc = dict()
        for item_fld in doc_param['fields']:  # перебор полей выходной таблицы
            doc.setdefault(item_fld['name'], list())
            # Формируем записи в выходном файле
            records = self._get_data_records(item_fld)
            records_exclude = set()
            for row in doc_param['rows_exclude']:
                records_exclude.add(row[0])
            for record in records:
                if not record['column'] or not record['pattern'] or not record['pattern'][0]:
                    continue
                col = record['column'][0]
                name_field = self._get_key(col[0])
                if not name_field:
                    continue
                for row in record['rows_exclude']:
                    records_exclude.add(row[0])
                rows = self._get_value_range(
                    record['row'], len(team[name_field]))
                for row in rows:  # обрабатываем все строки области данных
                    if len(team[name_field]) > row[0] and not row[0] in records_exclude:
                        for patt in record['pattern']:
                            x = self._get_fld_value(
                                team=team[name_field],
                                type_fld=record['type'],
                                pattern=patt, row=row[0])
                            if x:
                                record['value'] += x
                                if record['is_offset']:
                                    # если есть смещение, то берем данные от туда
                                    record['value_o'] = self._get_value_offset(
                                        team, record, row[0], col[0])
                                records_exclude.add(row[0])
                                break  # пропускаем проверку по остальным шаблонам
                if record['is_offset']:
                    record['value'] = record['value_o']
                    record['type'] = record['offset_type']
                if record['func']:
                    # запускаем функцию и передаем в нее полученное значение
                    record['value'] = self.func(
                        team=team, fld_param=record, data=record['value'], row=row[0], col=col[0])
                if record['value'] and not self._is_data_depends(record, doc, doc_param):
                    record['value'] = ''

                # формируем документ
                doc[record['name']].append(
                    {'row': len(doc[record['name']]), 'col': col[0], 'value': ''
                     if (isinstance(record['value'], int) or isinstance(record['value'], float))
                     and record['value'] == 0 else str(record['value'])})
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
        rows_required = self._get_required_rows(name, doc)
        rows_exclude = [x[0] if x[0] >= 0 else rows_count +
                        1+x[0] for x in doc_param['rows_exclude']]
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
                elif len(values) == 1 and values[0]['row'] == 0:
                    elem[key] = values[0]['value']
            if not is_empty and not (i in rows_exclude) and (not doc_param['required_fields'] or i in rows_required):
                self.append_to_collection(name, elem)

    def write_collections(self, num: int = 0, output_format: str = '') -> NoReturn:
        if not self.is_init() or len(self._collections) == 0:
            logging.warning('Не удалось прочитать данные из файла "{0}"\n'
                            'проверьте параметр "condition_begin_team": "{1}" '
                            .format(
                                self._parameters['filename']['value'][0], self._config._condition_team[0]
                                if self._config._condition_team else ''))
            return

        os.makedirs(self._parameters['path']['value'][0], exist_ok=True)

        id = self.func_id()
        for name, pages in self._collections.items():
            for key, records in pages.items():
                file_output = pathlib.Path(
                    self._parameters['path']['value'][0],
                    f'{self._parameters["inn"]["value"][0]}{"_"+str(num) if num != 0 else ""}' +
                    f'{"_"+key.replace(" ","_") if key != "noname" else ""}{id}_{name}')
                if not output_format or output_format == 'json':
                    with open(f'{file_output}.json', mode='a', encoding='utf-8') as file:
                        jstr = json.dumps(records, indent=4,
                                          ensure_ascii=False)
                        file.write(jstr)
                if not output_format or output_format == 'csv':
                    with open(f'{file_output}.csv', mode='a', encoding='utf-8') as file:
                        names = [x for x in records[0].keys()]
                        file_writer = csv.DictWriter(file, delimiter=";",
                                                     lineterminator="\r", fieldnames=names)
                        file_writer.writeheader()
                        for rec in records:
                            file_writer.writerow(rec)

    def write_logs(self, num: int = 0) -> NoReturn:
        if not self.is_init() or len(self._collections) == 0:
            return

        os.makedirs(PATH_LOG, exist_ok=True)

        id = self.func_id()

        i = 0
        file_output = pathlib.Path(
            PATH_LOG, f'{self._parameters["inn"]["value"][0]}{"_"+str(num) if num != 0 else ""}{id}')
        with open(f'{file_output}.log', 'w') as file:

            file.write(f'{{')
            for key, value in self._parameters.items():
                file.write(f'\t{key}:"')
                for val in value["value"]:
                    file.write(f'{val} ')
                file.write(f'",\n')
            file.write(f'}},\n')

            file.write(f'\n{{')
            for item in self._config._columns_heading:
                if item['row'] != -1:
                    file.write(
                        f"\t({item['col']}){item['name']}:  row={item['row']} col=")
                    for val in item["indexes"]:
                        file.write(f'{val},')
                    file.write(f'",\n')
            file.write(f'}},\n\n')

            file.write('\nself._parameters\n')
            jstr = json.dumps(self._parameters, indent=4)
            file.write(jstr)
            file.write('\nself._config._parameters\n')
            jstr = json.dumps(self._config._parameters, indent=4)
            file.write(jstr)
            file.write('\nself._config._columns_heading\n')
            jstr = json.dumps(self._config._columns_heading, indent=4)
            file.write(jstr)

# ---------- Параметры конфигурации --------------------

    def is_init(self) -> bool:
        return self._config._is_init

    def get_columns_heading(self, col: int = -1, name: str = '') -> list:
        if col != -1:
            if name:
                return self._config._columns_heading[col][name]
            else:
                return self._config._columns_heading[col]
        else:
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
        return self._get_value_int(self._config._page_index)

    def get_max_cols(self) -> int:
        return self._get_value_int(self._config._max_cols)[0]

    def get_row_start(self) -> int:
        return self._get_value_int(self._config._row_start)[0]

    def get_col_start(self) -> int:
        return self._config._col_start

    def set_col_start(self, col: int):
        self._config._col_start.append((col, True))

    def set_row_start(self, row: int):
        self._config._row_start = [(row, True)]

    def get_max_rows_heading(self) -> int:
        return self._get_value_int(self._config._max_rows_heading)[0]

    def get_header(self, name: str):
        return self._config._header[name]

    @warning_error
    def get_check(self, name: str):
        return self._config._check[name]

    def get_config_parameters(self, name: str = ''):
        if name:
            return self._config._parameters[name]
        else:
            return self._config._parameters

    def get_config_documents(self, name: str = ''):
        if name:
            return self._config._documents[name]
        else:
            return self._config._documents

    def init_data(self):
        self.colontitul['head'] = list()
        if self.colontitul['foot']:
            self.colontitul['head'].append(self.colontitul['foot'][-1])
        self.colontitul['foot'] = list()
        for col in self.get_columns_heading():
            col['active'] = False
        self._names = dict()
        self._teams = list()
# -------------------------------------------------------------------------------------------------

    def get_sub_value(self, item_fld, team, name_field, row, col, value):
        if item_fld['sub']:
            for item_sub in item_fld['sub']:
                value += self._get_fld_value(
                    team=team[name_field], type_fld=item_fld['type'], pattern=item_sub['pattern'][0], row=row)
                if value:
                    if item_sub['offset_row'] or item_sub['offset_column']:
                        try:
                            value = self._get_value_offset(
                                team=team, item_fld=item_sub, item_type=item_fld['type'], row_curr=row, col_curr=col, value=value)
                        except Exception as ex:
                            pass
                    if item_sub['func']:
                        value = self.func(
                            team=team, fld_param=item_sub, data=value, row=row, col=col)
                    return value
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
            'spacerem': self.func_spacerem,
            'spacerepl': self.func_spacerepl,
            'round2': self.func_round2,
            'opposite': self.func_opposite,
            'param': self.func_param,
            'id': self.func_id,
        }
        pattern = fld_param['func_pattern'][0]
        try:
            for name_func_add in fld_param['func'].split(','):
                value = 0 if fld_param['type'] == 'float' or fld_param['offset_type'] == 'float' else ''
                for name_func in name_func_add.split('+'):
                    name_func, data_calc, is_check = self.__get_func_name(
                        name_func=name_func, data=data)
                    try:
                        f = dic_f[name_func.strip()]
                    except Exception as ex:
                        return name_func
                    if is_check:
                        if f(data_calc, row, col, team):
                            value += data_calc + ' '
                    else:
                        x = f(data_calc, row, col, team)
                        if isinstance(value, float) or isinstance(value, int):
                            value += self._get_value(x, '.+', 'float')
                            value = round(value, 2)
                        else:
                            value += x + ' '
                data = str(value).strip()
                if pattern:
                    if isinstance(value, float):
                        data = data.replace(' ', '').replace(',', '.')
                    data = regular_calc(pattern, data)
                    pattern = ''  # шаблон проверки применятся только один раз
            return data.strip()
        except Exception as ex:
            return f'error {name_func}: {str(ex)}'

    def __get_func_name(self, name_func, data):
        is_check = False
        if name_func.find('(') != -1:
            # если функция с параметром, то заменяем входные данные (data) на этот параметр
            result = regular_calc(
                r'(?<=\()[\w_0-9-]+(?=\))', name_func)
            if result and result.find('error') == -1:
                data = result
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
            return self.get_columns_heading(col, 'name')
        return ''

    def func_column_value(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        value = next((x[row]['value']
                     for x in team.values() if x[row]['col'] == int(data)), '')
        # value = next((x[row]['value']
        #              for x in team.values() if x[row]['col'] == col+int(data)), '')
        return value

    def func_param(self, key: str = '', row: int = -1, col: int = -1, team: dict = {}):
        m = ''
        for item in self._parameters[key]['value']:
            m += (item.strip() + ' ') if isinstance(item, str) else ''
        return f'{m.strip()}'

    def func_spacerem(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        return data.replace(' ', '')

    def func_spacerepl(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        return data.replace(' ', '_')

    def func_round2(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        return str(round(data, 2)) if isinstance(data, float) else data

    def func_opposite(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        return str(-data) if isinstance(data, float) else data
