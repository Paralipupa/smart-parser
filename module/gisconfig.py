import configparser
from datetime import datetime
import os
import re
from typing import NoReturn
import logging


def check_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception as ex:
            logging.warning(
                'error in func: {}. skip :\n{}'.format(func, str(ex)))
            return None
    return wrapper


class GisConfig:

    def __init__(self, filename: str):
        self._is_init = False
        if not self.is_exist(filename):
            logging.warning('file not found {}. skip'.format(filename))
            return

        self._config = configparser.ConfigParser()
        self._config.read(filename)
        self.configuration_initialize()

    def is_exist(self, filename: str) -> bool:
        return os.path.exists(filename)

    @check_error
    def configuration_initialize(self) -> NoReturn:
        # регул.выражение начала новой области (иерархии)
        self._condition_team = ''
        self._condition_end_table = ''  # регул.выражение окончания табличных данных
        # регул.выражение колонки начала области (иерархии)
        self._condition_team_column = ''
        # колонка в которой просматривается условие окончания таблицы
        self._condition_end_table_column: int = ''
        # список заголовков колонок таблицы
        self._columns_heading: list[dict] = []
        self._row_start: int = self.read_config(
            'main', 'row_start', isNumeric=True)    #
        self._page_name: str = self.read_config('main', 'page_name')         #
        self._page_index: int = self.read_config(
            'main', 'page_index', isNumeric=True)  #
        # максимальное кол-во просматриваемых колонок
        self._max_cols: int = self.read_config(
            'main', 'max_columns', isNumeric=True)
        self._max_rows_heading: int = self.read_config(
            'main', 'max_rows_heading', isNumeric=True)  # максимальное кол-во строк до таблицы
        self.set_check()
        self.set_header()
        self.set_parameters()
        self.set_table_columns()
        self.set_documents()
        self._is_init = True

    def set_header(self):
        self._header = {'row': [0], 'col': [0], 'pattern': ''}
        self._header['row'] = self.read_config(
            'header', 'rows_count', isNumeric=True)
        self._header['col'] = self.read_config(
            'header', 'column', isNumeric=True)
        self._header['pattern'] = self.read_config('header', 'pattern')

    def set_check(self):
        self._check = {'row': [0], 'col': [0], 'pattern': ''}
        self._check['row'] = self.read_config('check', 'row', isNumeric=True)
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
            self._parameters[self.read_config(f'headers_{i}', 'name')].append(
                {
                    'row': self.read_config(f'headers_{i}', 'row', isNumeric=True),
                    'col': self.read_config(f'headers_{i}', 'column', isNumeric=True),
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
            self._parameters[self.read_config(f'footers_{i}', 'name')].append(
                {
                    'row': self.read_config(f'footers_{i}', 'row', isNumeric=True),
                    'col': self.read_config(f'footers_{i}', 'column', isNumeric=True),
                    'pattern': self.read_config(f'footers_{i}', 'pattern'),
                    'ishead': False,
                }
            )
            i += 1

    def set_table_columns(self) -> NoReturn:
        num_cols = self.read_config('main', 'columns_count', isNumeric=True)
        i = 0
        while self.read_config(f'col_{i}', 'pattern'):
            heading = {'name': self.read_config(f'col_{i}', 'pattern'),
                       'index': -1,
                       'row': -1,
                       'col': i,
                       'group_name': self.read_config(f'col_{i}', 'group'),
                       'active': False,
                       'offset': dict(),
                       }
            self._columns_heading.append(heading)
            self.set_conditions(i)
            self.set_heading_offset(i)
            i += 1

    def set_conditions(self, i: int) -> NoReturn:
        if not self._condition_team:
            self._condition_team = self.read_config(
                f'col_{i}', 'condition_begin_team')
            self._condition_team_column = self.read_config(
                f'col_{i}', 'pattern')
        if not self._condition_end_table:
            self._condition_end_table = self.read_config(
                f'col_{i}', 'condition_end_table')
            self._condition_end_table_column = self.read_config(
                f'col_{i}', 'pattern')

    def set_heading_offset(self, i: int):
        self._columns_heading[i]['offset']['row'] = self.read_config(
            f'col_{i}', 'row_offset', isNumeric=True)
        self._columns_heading[i]['offset']['col'] = self.read_config(
            f'col_{i}', 'col_offset', isNumeric=True)
        self._columns_heading[i]['offset']['pattern'] = self.read_config(
            f'col_{i}', 'pattern_offset')
        self._columns_heading[i]['offset']['is_include'] = False if self.read_config(f'col_{i}', 'is_include_offset') == '0' \
            else True

    @check_error
    def set_documents(self) -> NoReturn:
        self._documents = list()  # список документов
        k = 0
        while self.read_config(f'doc_{k}', 'name'):
            doc = dict()
            doc['name'] = self.read_config(f'doc_{k}', 'name')
            doc['rows_exclude'] = self.read_config(f'doc_{k}', 'rows_exclude',isNumeric=True)
            doc['required_fields'] = self.read_config(f'doc_{k}', 'required_fields')
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
            fld['column_offset'] = self.read_config(
                f'{doc["name"]}_{i}', 'col_offset', isNumeric=True)  # колонка для поиска данных аттрибут
            fld['pattern_offset'] = self.read_config(
                f'{doc["name"]}_{i}', 'pattern_offset')  # шаблон поиска (регулярное выражение)
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
            fld.append(
                {
                    'row': self.read_config(f'{name}_{i}_{j}', 'row', isNumeric=True),
                    'column': self.read_config(f'{name}_{i}_{j}', 'column', isNumeric=True),
                    'pattern': self.read_config(f'{name}_{i}_{j}', 'pattern'),
                    'column_offset': self.read_config(f'{name}_{i}_{j}', 'column_offset', isNumeric=True),
                    'pattern_offset': self.read_config(f'{name}_{i}_{j}', 'pattern_offset'),
                    'func': self.read_config(f'{name}_{i}_{j}', 'func'),
                    'func_pattern': self.read_config(f'{name}_{i}_{j}', 'func_pattern'),
                }
            )
            j += 1

    @check_error
    def get_range(self, x: str) -> list:
        return [int(i) for i in x.split(',')]

    def read_config(self, name_section: str, name_param: str, isNumeric: bool = False):
        try:
            result: str = self._config[name_section][name_param]
            if isNumeric:
                if result.find(',') != -1:
                    return self.get_range(result)
                elif result:
                    return [int(result)]
                else:
                    return []
            return result
        except:
            if isNumeric:
                return []
            else:
                return ''
