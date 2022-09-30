import configparser
from email.policy import strict
import os
import re
import traceback
from dataclasses import replace
from datetime import datetime
from typing import NoReturn, Union
from .settings import *


def fatal_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            db_logger.warning(traceback.format_exc())
            exit()
    return wrapper


def warning_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception as ex:
            return None
    return wrapper


def regular_calc(pattern, value):
    try:
        result = re.search(pattern, value.strip(), re.IGNORECASE)
        if not result:
            return ''
        else:
            return result.group(0).strip()
    except Exception as ex:
        return f"error in regular: '{pattern}' ({str(ex)})"

def print_message(msg: str, end: str = '', flush: bool = False):
    if IS_MESSAGE_PRINT:
        print(msg, end=end, flush=flush)

class GisConfig:

    @fatal_error
    def __init__(self, filename: str):
        self._is_init = False
        self._is_unique = False
        self._warning = list()
        if not os.path.exists(filename):
            self._warning.append('file not found {}. skip'.format(filename))
            return
        self._config = configparser.ConfigParser()
        self._config.read(filename)
        self._config_name = filename
        self.configuration_initialize()

    @fatal_error
    def configuration_initialize(self) -> NoReturn:
        # регул.выражение начала новой области (иерархии)
        self._condition_team = list()
        self._condition_end_table = ''  # регул.выражение окончания табличных данных
        # регул.выражение колонки начала области (иерархии)
        self._condition_team_column = ''
        # колонка в которой просматривается условие окончания таблицы
        self._condition_end_table_column: str = ''
        # список заголовков колонок таблицы
        self._columns_heading: list[dict] = []
        self._row_start = self.read_config(
            'main', 'row_start', isNumeric=True)    #
        self._col_start = self.read_config(
            'main', 'col_start', isNumeric=True)    #
        self._page_name = self.read_config('main', 'page_name')
        self._page_index = self.read_config(
            'main', 'page_index', isNumeric=True)  #
        # максимальное кол-во просматриваемых колонок
        self._max_cols = self.read_config(
            'main', 'max_columns', isNumeric=True)
        # максимальное кол-во строк до таблицы
        self._max_rows_heading = self.read_config(
            'main', 'max_rows_heading', isNumeric=True)
        # необрабатываемые строки таблицы
        self._rows_exclude = self.read_config(
            'main', 'rows_exclude', isNumeric=True)
        self.set_patterns()
        self.set_check()
        self.set_header()
        self.set_parameters()
        self.set_table_columns()
        self.set_documents()
        self._is_unique = len(self._page_name) != 0 or len(
            self._page_index) != 1 or self._page_index[0][0] != 0
        self._is_init = True

    def set_header(self):
        self._header = {'row': [0], 'col': [0], 'pattern': ''}
        self._header['col'] = self.read_config(
            'header', 'column', isNumeric=True)
        self._header['pattern'] = self.__get_pattern(
            self.read_config('header', 'pattern'))

    def set_check(self):
        self._check = dict()
        self._check['row'] = self.read_config(
            'check', 'row', isNumeric=True)
        self._check['col'] = self.read_config(
            'check', 'column', isNumeric=True)
        self._check['pattern'] = self.__get_pattern(
            self.read_config('check', 'pattern'))
        self._check['func'] = self.read_config('check', 'func')
        self._check['func_pattern'] = self.read_config('check', 'func_pattern')
        i = 0
        while self.read_config('check', f'pattern_{i}'):
            self._check[f'pattern_{i}'] = self.read_config(
                'check', f'pattern_{i}')
            i += 1

    @fatal_error
    def set_parameters(self):
        self._parameters = dict()
        self.set_param_colontitul('headers')
        self.set_param_colontitul('footers', False)
        self._parameters.setdefault(
            'period', [{'row': 0, 'col': 0, 'pattern': [''], 'ishead': True}])
        self._parameters.setdefault(
            'address', [{'row': 0, 'col': 0, 'pattern': [''], 'ishead': True}])
        self._parameters.setdefault(
            'path', [{'row': 0, 'col': 0, 'pattern': [f'@{PATH_OUTPUT}'], 'ishead': True}])

    def set_param_colontitul(self, name_part: str, is_head: bool = True) -> NoReturn:
        i = 0
        name = 'default'
        while name:
            name = self.read_config(f'{name_part}_{i}', 'name')
            if name:
                self._parameters.setdefault(name, [])
                self._parameters[name].append(
                    {
                        'row': self.read_config(f'{name_part}_{i}', 'row', isNumeric=True),
                        'col': self.read_config(f'{name_part}_{i}', 'column', isNumeric=True),
                        'pattern': [self.__get_pattern(self.read_config(f'{name_part}_{i}', 'pattern'))],
                        'offset_row': self.read_config(f'{name_part}_{i}', 'offset_row', isNumeric=True),
                        'offset_col': self.read_config(f'{name_part}_{i}', 'offset_col', isNumeric=True),
                        'offset_pattern': self.read_config(f'{name_part}_{i}', 'offset_pattern'),
                        'ishead': is_head,
                    }
                )
                j = 0
                p = 'default'
                while p:
                    p = self.read_config(f'{name_part}_{i}', f'pattern_{j}')
                    if p:
                        self._parameters[name][0]['pattern'].append(p)
                    j += 1
            i += 1

    def set_table_columns(self) -> NoReturn:
        i = -1
        pattern = 'default'
        name = 'default'
        while pattern or name:
            i += 1
            pattern = self.__get_pattern(
                self.read_config(f'col_{i}', 'pattern'))
            name = self.read_config(f'col_{i}', 'name')
            if pattern or name:
                b1 = True if self.read_config(
                    f'col_{i}', 'is_duplicate') in ('-1', '1', 'True', 'true') else False
                b2 = True if self.read_config(
                    f'col_{i}', 'is_optional') in ('-1', '1', 'True', 'true') else False
                b3 = True if self.read_config(
                    f'col_{i}', 'is_unique') in ('-1', '1', 'True', 'true') else False
                b4 = True if self.read_config(
                    f'col_{i}', 'is_only_after_stable') in ('-1', '1', 'True', 'true') else False
                b2 = b2 or b4 or not pattern
                heading = {
                    'name': name if name else f'col_{i}',
                    'pattern': list(),
                    'index': -1,
                    'indexes': [],
                    'row': -1,
                    'col': i,
                    'col_data': self.read_config(f'col_{i}', 'col_data_offset', isNumeric=True),
                    'active': False,
                    'duplicate': b1,
                    'optional': b2,
                    'unique': b3,
                    'after_stable': b4,
                    'left': self.read_config(f'col_{i}', 'border_column_left', isNumeric=True),
                    'right': self.read_config(f'col_{i}', 'border_column_right', isNumeric=True),
                    'offset': dict(),
                }
                heading['pattern'].append(pattern)
                j = -1
                pattern_dop = 'default'
                while pattern_dop:
                    j += 1
                    pattern_dop = self.__get_pattern(
                        self.read_config(f'col_{i}', f'pattern_{j}'))
                    if pattern_dop:
                        heading['pattern'].append(pattern_dop)
                self._columns_heading.append(heading)
                self.set_column_conditions(i)
                self.set_column_offset(i)

    def set_column_conditions(self, i: int) -> NoReturn:
        patt = self.__get_pattern(self.read_config(
            f'col_{i}', 'condition_begin_team'))
        if len(self._condition_team) == 0 and patt:
            self._condition_team.append(patt)
            j = 0
            while self.read_config(f'col_{i}', f'condition_begin_team_{j}'):
                self._condition_team.append(self.__get_pattern(self.read_config(
                    f'col_{i}', f'condition_begin_team_{j}')))
                j += 1
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

        self._columns_heading[i]['offset']['pattern'] = [self.read_config(
            f'col_{i}', 'offset_pattern')]
        if not self._columns_heading[i]['offset']['pattern'][0] and index != -1 and index < len(self._columns_heading):
            self._columns_heading[i]['offset']['pattern'] = self._columns_heading[index]['offset']['pattern']


# ========================= Шаблоны =======================================================


    @fatal_error
    def set_patterns(self) -> NoReturn:
        self._patterns = dict()  # список шаблонов
        name = 'default'
        k = -1
        while name and k < 1000:
            part = f'pattern{"_" if k>=0 else ""}{k if k>=0 else ""}'
            name = self.read_config(part, 'name')
            if name:
                self._patterns[name] = self.read_config(part, 'pattern')
            k += 1

# ========================= Документы =======================================================
    @fatal_error
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

    def set_doc_field(self, fld: dict, name: str, doc: dict) -> dict:
        # имя поля
        x = self.read_config(f'{name}', 'name')
        if x:
            fld['name'] = x
        else:
            fld.setdefault('name', x)
        # шаблон поиска (регулярное выражение)
        x = self.__get_pattern(self.read_config(f'{name}', 'pattern'), doc)
        if x:
            fld['pattern'] = [x]
        else:
            fld.setdefault('pattern', [x])
        j = 0
        while self.read_config(f'{name}', f'pattern_{j}'):
            fld['pattern'].append(self.__get_pattern(
                self.read_config(f'{name}', f'pattern_{j}'), doc))
            j += 1
        # колонка для поиска данных аттрибут
        x = self.read_config(
            f'{name}', 'col_config', isNumeric=True)
        if x:
            fld['column'] = x
        else:
            fld.setdefault('column', x)
        # тип данных в колонке
        x = self.read_config(f'{name}', 'type')
        if x:
            fld['type'] = x
        else:
            fld.setdefault('type', x)
        # запись (в области) для поиска данных атрибутта
        x = self.read_config(
            f'{name}', 'row_data', isNumeric=True)
        if x:
            fld['row'] = x
        else:
            fld.setdefault('row', x)
        # запись (в области) для исключения поиска данных атрибутта
        x = self.read_config(
            f'{name}', 'rows_exclude', isNumeric=True)
        if x:
            fld['rows_exclude'] = x
        else:
            fld.setdefault('rows_exclude', x)
        # номер записи в области(иерархии) для поиска данных аттрибут
        # признак смещения по строкам области (иерархии) True=абсолютное,
        x = self.read_config(
            f'{name}', 'offset_row_data', isNumeric=True)
        if x:
            fld['offset_row'] = x
        else:
            fld.setdefault('offset_row', x)
        # колонка для поиска данных аттрибут
        x = self.read_config(f'{name}', 'offset_col_config', isNumeric=True)
        if x:
            fld['offset_column'] = x
        else:
            fld.setdefault('offset_column', x)
        fld['is_offset'] = (len(fld['offset_column']) !=
                            0 or len(fld['offset_row']) != 0)
        # шаблон поиска (регулярное выражение)
        x = self.__get_pattern(self.read_config(
            f'{name}', 'offset_pattern'), doc)
        if x:
            fld['offset_pattern'] = [x]
        else:
            fld.setdefault('offset_pattern', [x])
        j = 0
        while self.read_config(f'{name}', f'offset_pattern_{j}'):
            fld['offset_pattern'].append(self.__get_pattern(
                self.read_config(f'{name}', f'offset_pattern_{j}'), doc))
            j += 1
        # тип данных в колонке смещения
        x = self.read_config(
            f'{name}', 'offset_type')
        if x:
            fld['offset_type'] = x
        else:
            fld.setdefault('offset_type', x)
        # Зависимость заполнения от значения в другой колонке
        x = self.read_config(
            f'{name}', 'depends_on')
        if x:
            fld['depends'] = x
        else:
            fld.setdefault('depends', x)
        # запись (в области) для поиска данных атрибутта
        x = self.read_config(f'{name}', 'func')
        if x:
            fld['func'] = x
        else:
            fld.setdefault('func', x)
        # шаблон поиска (регулярное выражение)
        x = self.__get_pattern(self.read_config(
            f'{name}', 'func_pattern'), doc)
        if x:
            fld['func_pattern'] = [x]
        else:
            fld.setdefault('func_pattern', [x])
        return fld

    @warning_error
    def set_fld_pattern_ref(self, fld: dict, doc: dict) -> NoReturn:
        fld['pattern'][0], fld['column'] = self.__get_pattern(
            fld['pattern'][0], doc, fld['column'])

    def set_document_fields(self, doc: dict) -> NoReturn:
        i = 0
        while self.read_config(f'{doc["name"]}_{i}', 'name'):
            fld = self.set_doc_field(dict(), f'{doc["name"]}_{i}', doc)
            fld['sub'] = []
            j = 0
            while self.read_config(f'{doc["name"]}_{i}_{j}', 'pattern') or self.read_config(f'{doc["name"]}_{i}_{j}', 'offset_pattern'):
                fld_sub = self.set_doc_field(
                    fld.copy(), f'{doc["name"]}_{i}_{j}', doc)
                fld_sub['sub'] = []
                fld['sub'].append(fld_sub)
                j += 1
            for col in fld['column'][1:]:
                fld_sub = fld.copy()
                fld_sub['column'] = [col]
                fld['sub'].append(fld_sub)
            doc['fields'].append(fld)
            i += 1
            if not self.read_config(f'{doc["name"]}_{i}', 'name'):
                i = 99
        for fld in doc['fields']:
            self.set_fld_pattern_ref(fld, doc)
            for fld_sub in fld['sub']:
                self.set_fld_pattern_ref(fld_sub, doc)

    def field_copy(self, fld: dict) -> dict:
        copy_fld = fld.copy()
        return copy_fld

    @fatal_error
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

        try:
            rows = [(int(i.replace('(', '').replace(')', '')),
                     False if not i or (i[0] == '+' or i[0] == '-') else True,
                     False if i.find('(') == -1 else True) for i in x.split(',')]
        except Exception as ex:
            rows = []
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

    def __get_pattern(self, patt: str, doc: dict = None, col: list = None) -> Union[str, tuple]:
        if patt[0:1] == '@':
            names: str = patt[1:]
            patt: str = ''
            if names:
                for name in names.split(','):
                    if self._patterns.get(name, ''):
                        patt = patt + \
                            (('|' if patt else '') +
                                self._patterns[name]) if patt.find(self._patterns[name]) == -1 else ''
                    elif doc:
                        n = int(name)
                        col = doc['fields'][n]['column'] if col != None else None
                        try:
                            for p in doc['fields'][n]['pattern']:
                                patt = patt + \
                                    (('|' if patt else '') +
                                     p) if patt.find(p) == -1 else ''
                        except Exception as ex:
                            db_logger.warning(
                                f'{self._config_name}(pattern=@{n}): {ex.args}')
                    else:
                        patt = f'@{name}'
            else:
                for p in self._condition_team:
                    patt = patt + \
                        (('|' if patt else '') +
                            p) if patt.find(p) == -1 else ''
        if doc and col:
            return patt, col
        else:
            return patt
