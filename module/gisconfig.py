import configparser
import os
import re
import logging
import traceback
from dataclasses import replace
from datetime import datetime
from typing import NoReturn

db_logger = logging.getLogger('parser')


def check_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception as ex:
            db_logger.warning(traceback.format_exc())
            exit()
    return wrapper


class GisConfig:

    @check_error
    def __init__(self, filename: str):
        self._is_init = False
        if not os.path.exists(filename):
            logging.warning('file not found {}. skip'.format(filename))
            return

        self._config = configparser.ConfigParser()
        self._config.read(filename)
        self.configuration_initialize()

    @check_error
    def configuration_initialize(self) -> NoReturn:
        # регул.выражение начала новой области (иерархии)
        self._condition_team = ''
        self._condition_end_table = ''  # регул.выражение окончания табличных данных
        # регул.выражение колонки начала области (иерархии)
        self._condition_team_column = ''
        # колонка в которой просматривается условие окончания таблицы
        self._condition_end_table_column: str = ''
        # список заголовков колонок таблицы
        self._columns_heading: list[dict] = []
        self._row_start = self.read_config(
            'main', 'row_start', isNumeric=True)    #
        self._page_name = self.read_config('main', 'page_name')         #
        self._page_index = self.read_config(
            'main', 'page_index', isNumeric=True)  #
        # максимальное кол-во просматриваемых колонок
        self._max_cols = self.read_config(
            'main', 'max_columns', isNumeric=True)
        self._max_rows_heading = self.read_config(
            'main', 'max_rows_heading', isNumeric=True)  # максимальное кол-во строк до таблицы
        self.set_check()
        self.set_header()
        self.set_parameters()
        self.set_table_columns()
        self.set_documents()
        self._is_init = True

    def set_header(self):
        self._header = {'row': [0], 'col': [0], 'pattern': ''}
        self._header['col'] = self.read_config(
            'header', 'column', isNumeric=True)
        self._header['pattern'] = self.read_config('header', 'pattern')

    def set_check(self):
        self._check = {'row': [0], 'col': [0], 'pattern': ''}
        self._check['row'] = self.read_config(
            'check', 'row', isNumeric=True)
        self._check['col'] = self.read_config(
            'check', 'column', isNumeric=True)
        self._check['pattern'] = self.read_config('check', 'pattern')

    @check_error
    def set_parameters(self):
        self._parameters = dict()
        self.set_param_headers()
        self.set_param_footers()
        self._parameters.setdefault(
            'period', [{'row': 0, 'col': 0, 'pattern': '', 'ishead': True}])
        self._parameters.setdefault(
            'address', [{'row': 0, 'col': 0, 'pattern': '', 'ishead': True}])
        self._parameters.setdefault(
            'path', [{'row': 0, 'col': 0, 'pattern': '@output', 'ishead': True}])

    def set_param_headers(self) -> NoReturn:
        i = 0
        while self.read_config(f'headers_{i}', 'name'):
            self._parameters.setdefault(
                self.read_config(f'headers_{i}', 'name'), [])
            rows = self.read_config(f'headers_{i}', 'row', isNumeric=True)
            cols = self.read_config(
                f'headers_{i}', 'column', isNumeric=True)
            self._parameters[self.read_config(f'headers_{i}', 'name')].append(
                {
                    'row': rows,
                    'col': cols,
                    'pattern': self.read_config(f'headers_{i}', 'pattern'),
                    'ishead': True,
                }
            )
            i += 1

    def set_param_footers(self) -> NoReturn:
        i = 0
        while self.read_config(f'footers_{i}', 'name'):
            self._parameters.setdefault(
                self.read_config(f'footers_{i}', 'name'), [])
            rows = self.read_config(f'footers_{i}', 'row', isNumeric=True)
            cols = self.read_config(
                f'footers_{i}', 'column', isNumeric=True)
            self._parameters[self.read_config(f'footers_{i}', 'name')].append(
                {
                    'row': rows,
                    'col': cols,
                    'pattern': self.read_config(f'footers_{i}', 'pattern'),
                    'ishead': False,
                }
            )
            i += 1

    def set_table_columns(self) -> NoReturn:
        i = 0
        while self.read_config(f'col_{i}', 'pattern'):
            b = True if self.read_config(f'col_{i}', 'is_duplicate')=='1' else False
            heading = {
                'name': self.read_config(f'col_{i}', 'name'),
                'pattern': self.read_config(f'col_{i}', 'pattern'),
                'index': -1,
                'indexes': [],
                'row': -1,
                'col': i,
                'active': False,
                'duplicate': b,
                'offset': dict(),
            }
            if not heading['name']: heading['name'] = f'col_{i}'
            self._columns_heading.append(heading)
            self.set_column_conditions(i)
            self.set_column_offset(i)
            i += 1

    def set_column_conditions(self, i: int) -> NoReturn:
        if not self._condition_team:
            self._condition_team = self.read_config(
                f'col_{i}', 'condition_begin_team')
            self._condition_team_column = self._columns_heading[i]['name']
        if not self._condition_end_table:
            self._condition_end_table = self.read_config(
                f'col_{i}', 'condition_end_table')
            self._condition_end_table_column = self._columns_heading[i]['name']

    def set_column_offset(self, i: int):
        ref = self.read_config(f'col_{i}', 'offset')
        index = -1
        if ref and len(ref) > 1 and ref[0] == '@':
            index = int(ref[1:])

        self._columns_heading[i]['offset']['row'] = self.read_config(
            f'col_{i}', 'offset_row', isNumeric=True)
        if not self._columns_heading[i]['offset']['row'] and index != -1 and index < len(self._columns_heading):
            self._columns_heading[i]['offset']['row'] = self._columns_heading[index]['offset']['row']

        self._columns_heading[i]['offset']['col'] = self.read_config(
            f'col_{i}', 'offset_col', isNumeric=True)
        if not self._columns_heading[i]['offset']['col'] and index != -1 and index < len(self._columns_heading):
            self._columns_heading[i]['offset']['col'] = self._columns_heading[index]['offset']['col']

        self._columns_heading[i]['offset']['pattern'] = self.read_config(
            f'col_{i}', 'offset_pattern')
        if not self._columns_heading[i]['offset']['pattern'] and index != -1 and index < len(self._columns_heading):
            self._columns_heading[i]['offset']['pattern'] = self._columns_heading[index]['offset']['pattern']

    @check_error
    def set_documents(self) -> NoReturn:
        self._documents = list()  # список документов
        k = 0
        while self.read_config(f'doc_{k}', 'name'):
            doc = dict()
            doc['name'] = self.read_config(f'doc_{k}', 'name')
            doc['rows_exclude'] = self.read_config(
                f'doc_{k}', 'rows_exclude', isNumeric=True)
            doc['required_fields'] = self.read_config(
                f'doc_{k}', 'required_fields')
            doc['fields'] = list()
            self.set_document_fields(doc)
            self._documents.append(doc)
            k += 1

    def set_document_fields(self, doc) -> NoReturn:
        i = 0
        while self.read_config(f'{doc["name"]}_{i}', 'name'):
            fld = dict()
            fld['name'] = self.read_config(
                f'{doc["name"]}_{i}', 'name')  # имя аттрибута
            # шаблон поиска (регулярное выражение)
            fld['pattern'] = self.read_config(f'{doc["name"]}_{i}', 'pattern')
            # колонка для поиска данных аттрибут
            fld['column'] = self.read_config(
                f'{doc["name"]}_{i}', 'col_config', isNumeric=True)
            # тип данных в колонке
            fld['type'] = self.read_config(
                f'{doc["name"]}_{i}', 'type')
            # запись (в области) для поиска данных атрибутта
            fld['row'] = self.read_config(
                f'{doc["name"]}_{i}', 'row_data', isNumeric=True)
            # запись (в области) для исключения поиска данных атрибутта
            fld['row_exclude'] = self.read_config(
                f'{doc["name"]}_{i}', 'row_data_exclude', isNumeric=True)
            # номер записи в области(иерархии) для поиска данных аттрибут
            # признак смещения по строкам области (иерархии) True=абсолютное,
            fld['offset_row'] = self.read_config(
                f'{doc["name"]}_{i}', 'offset_row_data', isNumeric=True)
            # колонка для поиска данных аттрибут
            fld['offset_column'] = self.read_config(
                f'{doc["name"]}_{i}', 'offset_col_config', isNumeric=True)
            # шаблон поиска (регулярное выражение)
            fld['offset_pattern'] = self.read_config(
                f'{doc["name"]}_{i}', 'offset_pattern')
            # тип данных в колонке смещения
            fld['offset_type'] = self.read_config(
                f'{doc["name"]}_{i}', 'offset_type')
            # запись (в области) для поиска данных атрибутта
            fld['func'] = self.read_config(f'{doc["name"]}_{i}', 'func')
            # шаблон поиска (регулярное выражение)
            fld['func_pattern'] = self.read_config(
                f'{doc["name"]}_{i}', 'func_pattern')
            fld['sub'] = []

            doc['fields'].append(fld)
            self.set_field_sub(fld['sub'], doc["name"], i)
            i += 1
        for fld in doc['fields']:
            if fld['pattern'][0:1] == "@":
                fld['pattern'] = doc['fields'][int(
                    fld['pattern'][1:])]['pattern']

    def set_field_sub(self, fld, name, i: int):
        j = 0
        while self.read_config(f'{name}_{i}_{j}', 'pattern'):
            rows = self.read_config(
                f'{name}_{i}_{j}', 'row', isNumeric=True)
            cols = self.read_config(
                f'{name}_{i}_{j}', 'column', isNumeric=True)
            cols_offset = self.read_config(
                f'{name}_{i}_{j}', 'offset_col_config', isNumeric=True)
            rows_offset = self.read_config(
                f'{name}_{i}_{j}', 'offset_row_data', isNumeric=True)
            fld.append(
                {
                    'row': rows,
                    'column': cols,
                    'pattern': self.read_config(f'{name}_{i}_{j}', 'pattern'),
                    'offset_column': cols_offset,
                    'offset_row': rows_offset,
                    'offset_pattern': self.read_config(f'{name}_{i}_{j}', 'offset_pattern'),
                    'func': self.read_config(f'{name}_{i}_{j}', 'func'),
                    'func_pattern': self.read_config(f'{name}_{i}_{j}', 'func_pattern'),
                }
            )
            j += 1

    @check_error
    def get_range(self, x: str) -> list:
        if not x:
            return []
        pattern = re.compile('[-0-9+]+<[-0-9+]+')
        results = pattern.findall(x)
        for result in results:
            n_start = re.findall('[-0-9+]+', result)[0]
            n_end = re.findall('[-0-9+]+', result)[1]
            y = ','.join([('+' if (x.find('+') != -1 or x.find('-') != -1) and i >= 0 else '')
                          + str(i) for i in range(int(n_start), int(n_end)+1)])
            x = x.replace(result, y)

        # rows = [int(i) for i in x.split(',')]
        rows = [(int(i), False if not i or (
            i[0] == '+' or i[0] == '-') else True) for i in x.split(',')]
        return rows

    def read_config(self, name_section: str, name_param: str, isNumeric: bool = False):
        try:
            result: str = self._config[name_section][name_param]
            if isNumeric:
                return self.get_range(result)
            return result
        except:
            if isNumeric:
                return []
            else:
                return ''
