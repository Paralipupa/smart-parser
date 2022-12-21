import re
import os
import hashlib
import datetime
import pathlib
import uuid
import csv
import json
from ast import Return
from typing import NoReturn, Union
from itertools import product
from .gisconfig import GisConfig, fatal_error, warning_error, regular_calc, print_message, PATH_LOG
from module.exceptions import InnMismatchException
from .file_readers import get_file_reader
from preliminary.utils import get_ident, get_reg
from .settings import *


def _hashit(s): return hashlib.sha1(s).hexdigest()


class ExcelBaseImporter:

    @fatal_error
    def __init__(self, file_name: str, config_file: str, inn: str, data: list = None):
        self.is_file_exists = True
        self.is_hash = True
        self.is_check = False
        self._teams = list()  # список областей с данными
        self._dictionary = dict()
        self._columns = dict()
        self._page_index = 0
        self._page_name = ''
        self._headers = data
        self.colontitul = {'status': 0, 'is_parameters': False, 'head': list(
        ), 'foot': list()}  # список  записей до и после табличных данных
        self._names = dict()  # колонки таблицы
        self._parameters = dict()  # параметры отчета (период, и др.)
        self._parameters['inn'] = {'fixed': True,
                                   'value': [inn if inn else '0000000000']}
        self._parameters['filename'] = {'fixed': True, 'value': [file_name]}
        self._parameters['config'] = {'fixed': True, 'value': [config_file]}
        self._collections = dict()  # коллекция выходных таблиц
        self._config = GisConfig(config_file)

    def check(self, is_warning: bool = False) -> bool:
        if not self.is_verify(self._parameters['filename']['value'][0]):
            return False
        self._headers = self._get_headers()
        if not self._headers:
            return False
        return self._check_controll(self._headers, is_warning)

    def _check_controll(self, headers: list, is_warning: bool = False) -> list:
        self.is_check = True
        is_check = False if self._config._check['pattern'][0]['pattern'] else True
        for row in range(self._config._max_rows_heading[0][0]):
            if row < len(headers):
                if not is_check:
                    for patt in self._config._check['pattern']:
                        if not patt['is_find']:
                            patt['is_find'] = any(
                                [re.search(patt['pattern'], x) for x in headers[row]])
                    is_check = all([x['is_find']
                                   for x in self._config._check['pattern']])
                names = self._get_names(headers[row])
                self.check_columns(names, row)
                if is_check and self.check_stable_columns() and self.check_condition_team(self.map_record(headers[row])):
                    self.is_check = False
                    return self._check_function()
        self.is_check = False
        if is_warning:
            self._config._warning.append('файл "{0}" не сооответствует шаблону "{1}". skip'.format(
                self._parameters['filename']['value'][0], self._parameters['config']['value'][0]))
        return False

    @fatal_error
    def is_verify(self, file_name: str) -> bool:
        if not self.is_init():
            return False
        if not os.path.exists(self._parameters['filename']['value'][0]):
            self._config._warning.append(
                f"ОШИБКА чтения файла {file_name}")
            self.is_file_exists = False
            return False
        return True

    @fatal_error
    def read(self) -> bool:
        if not self.is_verify(self._parameters['filename']['value'][0]):
            return False
        # print_message('Файл {} ({})'.format(
        #     self._parameters['filename']['value'][0], self._parameters['config']['value'][0]))
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
                self._page_name = page[POS_PAGE_VALUE] if not page[POS_PAGE_IS_FIX] else ''
                self._page_index = page[POS_PAGE_VALUE] if page[POS_PAGE_IS_FIX] else 0
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
                    if self.colontitul['status'] != 2:
                        # Область до или после таблицы
                        if not self.check_bound_row(row):
                            break
                        names = self._get_names(record)
                        self.check_colontitul(names, row, record)
                    if self.colontitul['status'] == 2:
                        # Табличная область данных
                        self.check_body(record, row)
                    row += 1
                    if row % 100 == 0:
                        print_message('         Обработано: {}                          \r'.format(
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
                v = record[index[POS_INDEX_VALUE]]
                is_empty = is_empty and (v == '' or v is None)
                result_record[key].append(
                    {'row': size, 'col': value['col'], 'index': index[POS_INDEX_VALUE], 'value': v, 'negative': index[POS_INDEX_IS_NEGATIVE]})
        return result_record if not is_empty else None

    def append_team(self, mapped_record: list) -> bool:
        if self.check_condition_team(mapped_record):
            self._teams.append(mapped_record)
            return True
        elif len(self._teams) != 0:
            for key in mapped_record.keys():
                size = self._teams[-1][key][-1]['row'] + 1
                for mr in mapped_record[key]:
                    self._teams[-1][key].append({'row': size,
                                                'col': mr['col'],
                                                 'index': mr['index'],
                                                 'value': mr['value'],
                                                 'negative': mr['negative']})
        return False

    def check_condition_team(self, mapped_record: list) -> bool:
        if not self.get_condition_team():
            return True
        if not mapped_record:
            return False
        b = False
        for p in self.get_condition_team():
            if mapped_record.get(p['col']):
                for patt in p['pattern']:
                    result = self._get_condition_data(
                        mapped_record[p['col']], patt)
                    b = False if not result or result.find(
                        'error') != -1 else True
                    if b:
                        if len(self._teams) != 0:
                            # Проверяем значение со значением из предыдущей области (иерархии)
                            # если не совпадает, то фиксируем начало новой области (иерархии)
                            pred = self._get_condition_data(
                                self._teams[-1][p['col']], patt)
                            b = (result != pred)
                        if b:
                            return b
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
                    for index in item['indexes']:
                        c += f"({item['row']},{index[POS_INDEX_VALUE]}) "
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
                    s += f"\n{key} - {value['indexes'][0][POS_INDEX_VALUE]}"
                self._config._warning.append('\n{0}:\nВ загружаемом файле "{1}" \
                \nне верен шаблон нахождения начала области данных(({3})condition_begin_team(\n{2}\n))\n{4}\n'
                                             .format(
                                                 self._config._config_name,
                                                 self._parameters['filename']['value'][0],
                                                 self.get_condition_team(
                                                 )[0]['pattern'] if self.get_condition_team() else '',
                                                 self.get_condition_team(
                                                 )[0]['col'] if self.get_condition_team() else '',
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
                    self.dynamic_change_config()
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
            last_cols = []
            # список уже добавленных колонок, которые нужно исключить при следующем прохождении
            cols_exclude = list()
            for x in [x['indexes'] for x in self._names.values()]:
                cols_exclude.extend([y[POS_INDEX_VALUE] for y in x])
            # сначала проверяем обязательные и приоритетные колонки
            for item in self.get_columns_heading():
                if (not item['active'] or item['duplicate']) and item['pattern'][0] and (not item['optional'] or item['priority']):
                    if self.check_column(item, names, row, cols_exclude):
                        is_find = True
            # потом проверяем остальные колонки
            for item in self.get_columns_heading():
                if (not item['active'] or item['duplicate']) and item['pattern'][0] and item['optional'] and not item['priority']:
                    if item['after_stable']:
                        last_cols.append(item)
                    elif self.check_column(item, names, row, cols_exclude):
                        is_find = True
            # последние колонки (after_stable = True)
            for item in last_cols:
                if self.check_stable_columns() and (row in self._get_rows_header() or item['duplicate']):
                    if self.check_column(item, names, row, cols_exclude, True):
                        is_find = True
        return is_find

    def check_column(self, item: dict, names: list, row: int, cols_exclude: list = [], is_last: bool = False) -> dict:
        is_find = False
        patt = ''
        for p in item['pattern']:
            patt = patt + ('|' if patt else '') + p
        search_names = self._get_search_names(
            names, patt, cols_exclude if not item['duplicate'] else [])  # колонки в таблице Excel
        if search_names:
            for search_name in search_names:
                b = True
                if item['offset']['pattern'][0]:
                    b = self.check_column_offset(item, search_name['col'])
                if b:
                    col_left = self._get_border(
                        item, 'left', search_name['col'])
                    col_right = self._get_border(
                        item, 'right', search_name['col'])
                    if col_left <= search_name['col'] <= col_right:
                        key = item['name']
                        self._names.setdefault(key, {'row': row,
                                                     'col': item['col'],
                                                     'active': True,
                                                     'indexes': []})
                        self._names[key]['active'] = True
                        item['active'] = True if not item['after_stable'] else False
                        if item['col_data']:
                            for val in item['col_data']:
                                index = val[POS_NUMERIC_VALUE] + \
                                    search_name['col'] if not val[POS_NUMERIC_IS_ABSOLUTE] else 0
                                # добавляем номер колонки в таблице с данными для суммирования значений
                                if not ((index, val[POS_NUMERIC_IS_NEGATIVE]) in self._names[key]['indexes']):
                                    item['indexes'].append(
                                        (index, val[POS_NUMERIC_IS_NEGATIVE]))
                                    self._names[key]['indexes'].append(
                                        (index, val[POS_NUMERIC_IS_NEGATIVE]))
                        else:
                            if not ((search_name['col'], False) in self._names[key]['indexes']):
                                item['indexes'].append(
                                    (search_name['col'], False))
                                self._names[key]['indexes'].append(
                                    (search_name['col'], False))
                                if is_last:
                                    self._columns[search_name['col']
                                                  ] = search_name['name']
                        item['row'] = row
                        is_find = True
                        if not is_last:
                            cols_exclude.append(search_name['col'])
                        else:
                            for x in cols_exclude:
                                while self._names[key]['indexes'].count((x, False)) > 0:
                                    self._names[key]['indexes'].remove(
                                        (x, False))
                                    item['indexes'].remove((x, False))
                                    self._columns.pop(x)
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
                    r = row[POS_NUMERIC_VALUE] if row[POS_NUMERIC_IS_ABSOLUTE] else (
                        row_count-1)+row[POS_NUMERIC_VALUE]
                    c = col[POS_NUMERIC_VALUE] if col[POS_NUMERIC_IS_ABSOLUTE] else index + \
                        col[POS_NUMERIC_VALUE]
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
                    key+'[а-я]{0,5}\s', item, re.IGNORECASE)), None)
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
    def _get_condition_data(self, values: list, pattern: str) -> str:
        result = ''
        for val in values:
            if val['row'] == 0:
                patt = pattern.split('|')[0] if result == '' else pattern
                value = regular_calc(patt, val['value'])
                if (value == '' and result == '' and pattern.find(r'^\s*$') != -1) or result.find('error') != -1:
                    return ''
                result += value
        return result

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

    def _get_border(self, item: dict, name: str, col: int = 0) -> int:
        if item[name]:
            name_field = self._get_key(item[name][0][POS_NUMERIC_VALUE])
            if name_field:
                col = self._names[name_field]['indexes'][0][POS_INDEX_VALUE]
            else:
                col = col + 1 if name == 'left' else col - 1
                if not self.is_check:
                    self._config._warning.append(
                        f'"{item["name"]}" - не найдена граница border_column_{name}={item[name][0][POS_NUMERIC_VALUE]}')
        return col

    def _get_rows_header(self) -> set:
        return {x['row'] for x in self._names.values()}

    def _get_check_pattern(self) -> list:
        rows: list[int] = self.get_check('row')  # раздел [check]
        if not rows:
            rows.append((0, False))
        patts = list()
        p = self.get_check('pattern')  # раздел [check]
        patts.append({'pattern': p, 'full': True,
                     'find': p == '', 'maxrow': rows[-1][0]})
        i = 0
        p = self.get_check(f'pattern_{i}')  # раздел [check]
        while p:
            p = self.get_check(f'pattern_{i}')
            patts.append({'pattern': p, 'full': True,
                         'find': False, 'maxrow': rows[-1][0]})
            i += 1
            p = self.get_check(f'pattern_{i}')

        # разделы [col_]
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

    def _check_function(self) -> bool:
        f = self._config._check['func']
        if not f:
            return True
        patt = [self._config._check['func_pattern']]
        item_fld = {'func': f, 'func_pattern': patt, 'is_offset': False,
                    'type': '', 'offset_type': '', 'value': '', 'value_o': ''}
        value = self.func(
            team=dict(), fld_param=item_fld, row=0, col=0)
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

    def _get_names(self, record: list) -> dict:
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
                value = str(self._get_int(value))
            elif type_value == 'double' or type_value == 'float':
                value = str(self._get_float(value))
        except:
            pass
        result: str = regular_calc(pattern, value)
        try:
            if type_value == 'int':
                result = self._get_int(value)
            elif type_value == 'double' or type_value == 'float':
                result = self._get_float(result)
            else:
                result = result.rstrip() + ' '
        except:
            result = 0
        return result

    def _get_value_str(self, value: str, pattern: str) -> str:
        return regular_calc(pattern, value)

    def _get_value_int(self, value: Union[list, str]) -> int:
        try:
            if value:
                if isinstance(value, list):
                    return value[0]
                elif isinstance(value, str):
                    return int(value.replace(',', '.').replace(' ', '')).replace(chr(160), '')
            else:
                return 0
        except:
            return 0

    def _get_float(self, value: str) -> float:
        try:
            if value:
                if isinstance(value, str):
                    return float(value.replace(',', '.').replace(' ', '').replace(chr(160), ''))
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

    def _get_fld_records(self, item_fld: dict):
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

    def _get_values(self, values: list, type_fld: str, pattern: str) -> str:
        value = self._get_value(type_value=type_fld)
        for val in values:
            if (type_fld == 'int' or type_fld == 'float') and val[POS_NUMERIC_IS_NEGATIVE]:
                value -= self._get_value(
                    val[POS_VALUE], pattern, type_fld)
            else:
                value += self._get_value(
                    val[POS_VALUE], pattern, type_fld)
        if not (type_fld == 'float' or type_fld == 'double' or type_fld == 'int'):
            value = value.lstrip()
        return value

    # данные из колонки по смещению (offset_column_)
    def _get_value_offset(self, team, record: dict, row_curr: int, col_curr: int) -> Union[str, int, float]:
        rows: list = record['offset_row']
        cols: list = record['offset_column']
        value: str = record['value_o']
        if not rows:
            rows = [(0, False)]
        if not cols:
            cols = [(col_curr, True)]
        fld_name: str = self._get_key(cols[0][POS_NUMERIC_VALUE])
        if fld_name:
            row = rows[0][POS_NUMERIC_VALUE] + \
                row_curr if not rows[0][POS_NUMERIC_IS_ABSOLUTE] else rows[0][POS_NUMERIC_VALUE]
            x = self._get_values(
                values=[(x['value'], None, x['negative']) for x in team[fld_name]
                        if x['row'] == row],
                type_fld=record['offset_type'],
                pattern=record['offset_pattern'][0]
            )
            value += x if not isinstance(x, str) or value.find(x) == -1 else ''
        return value

    def _get_required_rows(self, name: str, doc: dict) -> set:
        s = set()
        d = next(
            (x for x in self.get_config_documents() if x['name'] == name), None)
        if d and d['required_fields']:
            for name_field in d['required_fields'].split(','):
                fld_type = next((x['type']+x['offset_type']
                                for x in d['fields'] if x['name'] == name_field), '')
                for item in doc[name_field]:
                    val = self._get_value(str(item['value']), '.+', fld_type)
                    if ((fld_type=='' or fld_type=='str') and val.strip() != '') or ((fld_type=='float' or fld_type=='int') and val != 0):
                        s.add(item['row'])
        return s

    def _is_data_depends(self, record: dict, doc: dict, doc_param: dict) -> Union[str, bool]:
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
            self._parameters['path']['value'].append(PATH_OUTPUT)
        self._parameters.setdefault(
            'address', {'fixed': False, 'value': list()})
        if not self._parameters['address']['value']:
            self._parameters['address']['value'].append('')
        self.colontitul['is_parameters'] = True
        if self._parameters['inn']['value'][0] != '0000000000' and self._config._parameters.get('inn'):
            l = [x for x in self._config._parameters['inn'] if x['pattern'][0].find(self._parameters['inn']['value'][0]) !=-1 ]
            if not l:
                raise InnMismatchException

    def _set_parameter(self, name: str):
        for param in self.get_config_parameters(name):
            rows = param['row']
            cols = param['col']
            patterns = param['pattern']
            is_head = param['ishead']
            func = param.get('func')
            self._parameters.setdefault(
                name, {'fixed': False, 'value': list()})
            if func:
                value = self.func(fld_param={'func': func})
                if value:
                    self._parameters[name]['value'].append(value)
            else:
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
                                            param['offset_row'].append(
                                                (0, False))
                                        if not param['offset_col']:
                                            param['offset_col'].append(
                                                (0, False))
                                        result = self._get_value_after_validation(param['offset_pattern'],
                                                                                  'head' if is_head else 'foot',
                                                                                  param['offset_row'][0][POS_NUMERIC_VALUE] +
                                                                                  row[0] if not param['offset_row'][0][POS_NUMERIC_IS_ABSOLUTE] else param[
                                            'offset_row'][0][POS_NUMERIC_VALUE],
                                            param['offset_col'][0][POS_NUMERIC_VALUE] + col[0] if not param['offset_col'][0][POS_NUMERIC_IS_ABSOLUTE] else param['offset_col'][0][POS_NUMERIC_VALUE])
                                    if result:
                                        self._parameters[name]['value'].append(
                                            param['value'] if param.get('value') else result)
                                        break

        return self._parameters[name]

    def change_pp(self):
        if len(self._columns) == 0:
            return
        docs = [x for x in self._config._documents if x['name']
                in ('pp_charges', 'pp_service')]
        for doc in docs:
            flds = [x for x in doc['fields'] if x['name'] in (
                'internal_id', 'calc_value', 'tariff', 'service_internal_id', 'recalculation', 'accounting_period_total', 'name', 'kind')]
            for fld in flds:
                if fld['sub']:
                    ls = []
                    for key, name in self._columns.items():
                        ls.append(fld['sub'][-1].copy())
                        ls[-1]['func'] = ls[-1]['func'].replace('Прочие', name)
                        if len(fld['sub'][-1]['offset_column']) > 0:
                            l = [
                                x for x in self._config._columns_heading if x['name'] == get_ident(name)]
                            if l:
                                ls[-1]['offset_column'] = [
                                    (l[0]['col'], True, False)]
                    fld['sub'][-1]['offset_column'] = [(-1, True, False)]
                    fld['sub'].extend(ls)

    def change_heading(self):
        for key, name in self._columns.items():
            l = self._config._columns_heading[-1].copy()
            l['name'] = get_ident(name)
            l['pattern'] = [get_reg(name)]
            l['indexes'] = [(key, False)]
            l['col'] = len(self._config._columns_heading)
            l['after_stable'] = False
            l['duplicate'] = False
            l['activate'] = True
            self._config._columns_heading.append(l)
            self._names[l['name']] = {'row': l['row'],
                                      'col': l['col'],
                                      'active': True,
                                      'indexes': l['indexes']}

    def dynamic_change_config(self):
        self.change_heading()
        self.change_pp()

    def process_record(self, team: dict) -> NoReturn:
        if not self.colontitul['is_parameters']:
            self._set_parameters()
        for doc_param in self.get_config_documents():
            doc = self.set_document(team, doc_param)
            self.document_split_one_line(doc, doc_param)
        self._teams.remove(team)

################################################################################################################################################
# --------------------------------------------------- Документы --------------------------------------------------------------------------------
################################################################################################################################################
    def append_to_collection(self, name: str, doc: dict) -> NoReturn:
        key = self._page_name if self._page_name else 'noname'
        self._collections.setdefault(name, {key: list()})
        self._collections[name].setdefault(key, list())
        self._collections[name][key].append(doc)
        if self.get_doc_type(name) == 'dictionary' and doc.get('key') and doc.get('value'):
            self._dictionary[self.func_hash(doc['key'])] = doc['value']

# Формирование документа из полученной порции (отдельной области или иерархии)
    def set_document(self, team: dict, doc_param):
        doc = dict()
        for fld_item in doc_param['fields']:  # перебор полей выходной таблицы
            # Формируем записи в выходном файле
            doc.setdefault(fld_item['name'], list())
            main_rows_exclude = set()
            offset_rows_exclude = set()
            for table_row in doc_param['rows_exclude']:
                main_rows_exclude.add((table_row[0], -1))
            # собираем все поля (sub): name_attr, name_attr_0, ... , name_attr_N
            fld_records = self._get_fld_records(fld_item)
            for fld_record in fld_records:
                if not fld_record['column'] or not fld_record['pattern'] or not fld_record['pattern'][0]:
                    continue
                col = fld_record['column'][0]
                name_field = self._get_key(col[POS_VALUE])
                if not name_field:
                    continue
                for table_row in fld_record['rows_exclude']:
                    main_rows_exclude.add((table_row[0], -1))
                table_rows = self._get_value_range(
                    fld_record['row'], len(team[name_field]))
                for table_row in table_rows:  # обрабатываем все строки области данных
                    if len(team[name_field]) > table_row[0] and not (table_row[0], -1) in main_rows_exclude \
                            and not (table_row[POS_VALUE], col[POS_VALUE]) in main_rows_exclude:
                        for patt in fld_record['pattern']:
                            x = self._get_values(
                                values=[(x['value'], None, x['negative']) for x in team[name_field]
                                        if x['row'] == table_row[POS_VALUE]],
                                type_fld=fld_record['type'],
                                pattern=patt)
                            if x:
                                fld_record['value'] += x if not isinstance(
                                    x, str) or fld_record['value'].find(x) == -1 else ''
                                if fld_record['is_offset']:
                                    if not (table_row[POS_VALUE], col[POS_VALUE], fld_record['offset_column'][0][POS_VALUE]) \
                                            in offset_rows_exclude:
                                        # если есть смещение, то берем данные от туда
                                        fld_record['value_o'] = self._get_value_offset(
                                            team, fld_record, table_row[0], col[POS_VALUE])
                                        offset_rows_exclude.add(
                                            (table_row[POS_VALUE], col[POS_VALUE], fld_record['offset_column'][0][POS_VALUE]))
                                else:
                                    main_rows_exclude.add(
                                        (table_row[0], col[POS_VALUE]))
                                break  # пропускаем проверку по остальным шаблонам
                if fld_record['func']:
                    # запускаем функцию
                    fld_record['value'] = self.func(
                        team=team, fld_param=fld_record, row=table_row[0], col=col[0])
                elif fld_record['is_offset']:
                    fld_record['value'] = fld_record['value_o']
                    fld_record['type'] = fld_record['offset_type']
                if fld_record['value'] and not self._is_data_depends(fld_record, doc, doc_param):
                    fld_record['value'] = ''
                # формируем документ
                doc[fld_record['name']].append(
                    {'row': len(doc[fld_record['name']]), 'col': col[0], 'value': ''
                     if ((isinstance(fld_record['value'], int) or isinstance(fld_record['value'], float))
                     and fld_record['value'] == 0) or
                     (isinstance(fld_record['value'], str)
                      and fld_record['offset_type'] == 'float' and fld_record['value'] == '0.0')
                     else str(fld_record['value']).strip()})
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

################################################################################################################################################
# --------------------------------------------------- Запись в файл ----------------------------------------------------------------------------
################################################################################################################################################
    def write_collections(self, num: int = 0, path_output: str = 'output', output_format: str = '') -> NoReturn:
        if not self.is_init() or len(self._collections) == 0:
            logging.warning('Не удалось прочитать данные из файла "{0} - {1}"\n'
                            .format(self.func_inn(),
                                    self._parameters['filename']['value'][0]))
            return

        os.makedirs(path_output, exist_ok=True)

        self._current_value = ''
        id = self.func_id()
        inn = self.func_inn()
        for name, pages in self._collections.items():
            for key, records in pages.items():
                file_output = pathlib.Path(
                    path_output,
                    f'{inn}{"_"+str(num) if num != 0 else ""}' +
                    f'{"_"+key.replace(" ","_") if key != "noname" else ""}{id}_{name}')
                if not output_format or output_format == 'json':
                    with open(f'{file_output}.json', mode='w', encoding=ENCONING) as file:
                        jstr = json.dumps(records, indent=4,
                                          ensure_ascii=False)
                        file.write(jstr)

                if not output_format or output_format == 'csv':
                    with open(f'{file_output}.csv', mode='w', encoding=ENCONING) as file:
                        names = [x for x in records[0].keys()]
                        file_writer = csv.DictWriter(file, delimiter=";",
                                                     lineterminator="\r", fieldnames=names)
                        file_writer.writeheader()
                        for rec in records:
                            file_writer.writerow(rec)

    def write_logs(self, num: int = 0, path_output: str = 'logs') -> NoReturn:
        if not self.is_init() or len(self._collections) == 0:
            return
        os.makedirs(path_output, exist_ok=True)
        id = self.func_id()
        inn = self.func_inn()
        i = 0
        file_output = pathlib.Path(
            path_output, f'{inn}{"_"+str(num) if num != 0 else ""}{id}')
        with open(f'{file_output}.log', 'w', encoding=ENCONING) as file:
            file.write(f'{{')
            for key, value in self._parameters.items():
                file.write(f'\t{key}:"')
                for index in value["value"]:
                    file.write(f'{index} ')
                file.write(f'",\n')
            file.write(f'}},\n')
            file.write(f'\n{{')
            for item in self._config._columns_heading:
                if item['row'] != -1:
                    file.write(
                        f"\t({item['col']}){item['name']}:  row={item['row']} col=")
                    for index in item["indexes"]:
                        file.write(f'{index[POS_INDEX_VALUE]},')
                    file.write(f'",\n')
            file.write(f'}},\n\n')
            file.write('\nself._parameters\n')
            jstr = json.dumps(self._parameters, indent=4, ensure_ascii=False)
            file.write(jstr)
            file.write('\nself._config._parameters\n')
            jstr = json.dumps(self._config._parameters, indent=4)
            file.write(jstr)
            file.write('\nself._config._columns_heading\n')
            jstr = json.dumps(self._config._columns_heading,
                              indent=4, ensure_ascii=False)
            file.write(jstr)

################################################################################################################################################
# ---------------------------------------------- Параметры конфигурации ------------------------------------------------------------------------
################################################################################################################################################

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

    def get_doc_type(self, name: str) -> str:
        return ''.join([x['type'] for x in self._config._documents if x['name'] == name])

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

################################################################################################################################################
# ----------------------------------------------------- Функции --------------------------------------------------------------------------------
################################################################################################################################################

    def func(self, team: dict = {}, fld_param: dict = {}, row: int = 0, col: int = 0) -> str:
        dic_f = {
            'inn': self.func_inn,
            'period_first': self.func_period_first,
            'period_last': self.func_period_last,
            'period_month': self.func_period_month,
            'period_year': self.func_period_year,
            'column_name': self.func_column_name,
            'column_value': self.func_column_value,
            'hash': self.func_hash,
            'guid': self.func_uuid,
            'param': self.func_param,
            'spacerem': self.func_spacerem,
            'spacerepl': self.func_spacerepl,
            'round2': self.func_round2,
            'round4': self.func_round4,
            'round6': self.func_round6,
            'opposite': self.func_opposite,
            'param': self.func_param,
            'dictionary': self.func_dictionary,
            'to_date': self.func_to_date,
            'id': self.func_id,
        }
        self._current_value = fld_param.get('value', '')
        pattern = fld_param['func_pattern'][0] if fld_param.get(
            'func_pattern') else ''
        data = fld_param.get('value_o', '') if fld_param.get(
            'is_offset') else fld_param.get('value', '')
        try:
            for name_func_add in fld_param.get('func', '').split(','):
                value = 0 if fld_param.get('type', 'str') == 'float' or fld_param.get(
                    'offset_type', 'str') == 'float' else ''
                for index, name_func in enumerate(re.split(r"[+-]", name_func_add)):
                    name_func, data_calc, is_check = self.__get_func_name(
                        name_func=name_func, data=data, dic_f=dic_f)
                    try:
                        f = dic_f[name_func.strip()]
                    except Exception as ex:
                        if self._parameters.get(name_func, []):
                            value = value.strip() + \
                                (self._parameters[name_func]['value'][-1]
                                 if self._parameters[name_func]['value'] else '')
                        elif name_func == '_':
                            value = value.strip() + (' ' if value else '') + data
                        else:
                            value = value.strip() + (' ' if value else '') + name_func
                    else:
                        if is_check:
                            if f(data_calc, row, col, team):
                                value += data_calc + ' '
                        else:
                            x = f(data_calc, row, col, team)
                            if isinstance(value, float) or isinstance(value, int):
                                if name_func_add.find(f'-{name_func}') != -1 and index != 0:
                                    value -= self._get_value(x, '.+', 'float')
                                else:
                                    value += self._get_value(x, '.+', 'float')
                            else:
                                value += x + ' '
                data = str(value).strip()
                self._current_value = data
                if pattern:
                    if isinstance(value, float):
                        data = data.replace(' ', '').replace(',', '.')
                    data = regular_calc(pattern, data)
                    pattern = ''  # шаблон проверки применятся только один раз
            return data.strip()
        except Exception as ex:
            return f'error {name_func}: {str(ex)}'

    def __get_func_name(self, name_func: str, data: str, dic_f: dict):
        is_check = False
        if name_func.find('(') != -1 and name_func.find(' (') == -1:
            # если функция с параметром, то заменяем входные данные (data) на этот параметр
            result = regular_calc(
                r'(?<=\()[a-zA-Zа-яА-Я_0-9-]+(?=\))', name_func) if name_func.find(' (') == -1 else ''
            if result and result.find('error') == -1:
                data = result
            try:
                f = dic_f[name_func[:name_func.find('(')]]
                name_func = name_func[:name_func.find('(')]
            except:
                # name_func = name_func.replace('(', '- ').replace(')', '')
                pass
        if name_func.find('check_') != -1:
            name_func = name_func.replace('check_', '')
            is_check = True
        return name_func, data, is_check

    def func_inn(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        if self._parameters['inn']['value'][0] != '0000000000':
            return self._parameters['inn']['value'][0]
        else:
            return self._parameters['inn']['value'][-1]

    def func_period_first(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        period = datetime.datetime.strptime(
            self._parameters['period']['value'][-1], '%d.%m.%Y')
        return period.replace(day=1).strftime('%d.%m.%Y')

    def func_period_last(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        period = datetime.datetime.strptime(
            self._parameters['period']['value'][-1], '%d.%m.%Y')
        next_month = period.replace(day=28) + datetime.timedelta(days=4)
        return (next_month - datetime.timedelta(days=next_month.day)).strftime('%d.%m.%Y')

    def func_period_month(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return self._parameters['period']['value'][0][3:5]

    def func_period_year(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return self._parameters['period']['value'][0][6:]

    def func_to_date(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        patts = ['%d-%m-%Y', '%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d',
                 '%d-%m-%y', '%d.%m.%y', '%d/%m/%y', '%B %Y']
        for p in patts:
            try:
                d = datetime.datetime.strptime(data, p)
                return data
            except:
                pass
        return ''

    def func_hash(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return _hashit(str(data).encode('utf-8')) if self.is_hash else data

    def func_uuid(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        return str(uuid.uuid5(uuid.NAMESPACE_X500, data))

    def func_id(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        d = self._parameters['period']['value'][0]
        return f'{str(self._current_value).strip()}_{d[3:5]}{d[6:]}'  # _mmyyyy

    def func_column_name(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        if col != -1:
            return self.get_columns_heading(col, 'alias')
        return ''

    def func_column_value(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        value = next((x[row]['value']
                     for x in team.values() if x[row]['col'] == int(data)), '')
        return value

    def func_param(self, data: str = '', row: int = -1, col: int = -1, team: dict = {}):
        m = ''
        for item in self._parameters[data]['value']:
            m += (item.strip() + ' ') if isinstance(item, str) else ''
        return f'{m.strip()}'

    def func_spacerem(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        return data.strip().replace(' ', '')

    def func_spacerepl(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        return data.strip().replace(' ', '_')

    def func_round2(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        return str(round(data, 2)) if isinstance(data, float) else data

    def func_round4(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        return str(round(data, 4)) if isinstance(data, float) else data

    def func_round6(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        return str(round(data, 6)) if isinstance(data, float) else data

    def func_opposite(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        return str(-data) if isinstance(data, float) else data

    def func_dictionary(self, data: str = '', row: int = -1, col: int = 0, team: dict = {}):
        return self._dictionary.get(data, '')
        # return data+'('+self._dictionary.get(data,'')+')'
