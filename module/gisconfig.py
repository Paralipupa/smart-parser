import configparser
import os
from typing import NoReturn
import logging

def check_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except:
            logging.warning('error in func: {}. skip'.format(func))
            return None
    return wrapper

class GisConfig:

    def __init__(self, filename : str):
        self._is_init = False
        if not self.is_exist(filename):
            logging.warning('file not found {}. skip'.format(filename))
            return

        self._config = configparser.ConfigParser()
        self._config.read(filename)
        self.configuration_initialize()


    def is_exist(self, filename : str) -> bool:
        return os.path.exists(filename)

    @check_error
    def configuration_initialize(self) -> NoReturn:
        self._condition_team:str = ''  #условие начала новой области (регулярное выражение)
        self._condition_end_table:str = ''  #условие окончания табличных данных (регулярное выражение)
        self._condition_team_column:int = '' # колонка в которой просматривается условие области
        self._condition_end_table_column:int = '' # колонка в которой просматривается условие окончания таблицы
        self._columns_heading:list[dict] = []  # список заголовков колонок таблицы
        self._row_start:int = self.read_config('main','row_start',isNumeric=True)    #
        self._page_name:str = self.read_config('main','page_name')         #
        self._page_index:int = self.read_config('main','page_index',isNumeric=True)  #
        self._max_cols:int = self.read_config('main','max_columns',isNumeric=True)   #максимальное кол-во просматриваемых колонок
        self._max_rows_heading:int = self.read_config('main','max_rows_heading',isNumeric=True) #максимальное кол-во строк до таблицы
        self._documents:list[dict] = [] #список документов (настроек)
        self._parameters = dict()

        self.set_parameters()

        num_cols = self.read_config('main','columns_count',isNumeric=True)
        self._columns_heading = [{'name':self.read_config(f'col_{i}',
                                'pattern'),
                                'index':-1,
                                'row':-1,
                                'col':i,
                                'active':False,
                                'offset':dict(),
                                }
                                for i in range(num_cols[0])]
        for i in range(num_cols[0]):
            self.set_conditions(i)
            self.set_heading_offset(i)


        num_cols = self.read_config('main','documents_count',isNumeric=True)
        for i in range(num_cols[0]):
            self.set_documents(i)

        self.set_check()
        self.set_header()

        self._is_init = True


    def set_header(self):
        self._header = {'row':[0], 'col':[0], 'pattern':''}
        self._header['row'] = self.read_config('header','rows_count',isNumeric=True)
        self._header['col'] = self.read_config('header','column',isNumeric=True)
        self._header['pattern'] = self.read_config('header','pattern')


    def set_check(self):
        self._check = {'row':[0], 'col':[0], 'pattern':''}
        self._check['row'] = self.read_config('check','row',isNumeric=True)
        self._check['col'] = self.read_config('check','column',isNumeric=True)
        self._check['pattern'] = self.read_config('check','pattern')

    @check_error
    def set_parameters(self):
        self._parameters['period'] = [{'row':0, 'col':0, 'pattern':'', 'ishead': True}]
        self._parameters['address'] = [{'row':0, 'col':0, 'pattern':'', 'ishead': True}]
        self._parameters['path'] = [{'row':0, 'col':0, 'pattern':'@'+self.read_config('main','path_output'), 'ishead': True}]
        num_parms = self.read_config('main','headers_count',isNumeric=True)
        if num_parms:
            for i in range(num_parms[0]):
                self._parameters.setdefault(self.read_config(f'headers_{i}','name'), [])
                self._parameters[self.read_config(f'headers_{i}','name')].append(
                    {
                    'row' : self.read_config(f'headers_{i}','row',isNumeric=True),
                    'col' : self.read_config(f'headers_{i}','column',isNumeric=True),
                    'pattern' : self.read_config(f'headers_{i}','pattern'),
                    'ishead' : True,
                    }
                )
        num_parms = self.read_config('main','footers_count',isNumeric=True)
        if num_parms:
            for i in range(num_parms[0]):
                self._parameters.setdefault(self.read_config(f'footers_{i}','name'), [])
                self._parameters[self.read_config(f'footers_{i}','name')].append(
                    {
                    'row' : self.read_config(f'footers_{i}','row',isNumeric=True),
                    'col' : self.read_config(f'footers_{i}','column',isNumeric=True),
                    'pattern' : self.read_config(f'footers_{i}','pattern'),
                    'ishead' : False,
                    }
                )


    def set_conditions(self, i:int) -> NoReturn:
        if not self._condition_team:
            self._condition_team = self.read_config(f'col_{i}','condition_begin_team')
            self._condition_team_column = self.read_config(f'col_{i}','pattern')
        if not self._condition_end_table:
            self._condition_end_table = self.read_config(f'col_{i}','condition_end_table')
            self._condition_end_table_column = self.read_config(f'col_{i}','pattern')


    def set_heading_offset(self, i:int):
        self._columns_heading[i]['offset']['row'] = self.read_config(f'col_{i}','row_offset',isNumeric=True)
        self._columns_heading[i]['offset']['col'] = self.read_config(f'col_{i}','col_offset',isNumeric=True)
        self._columns_heading[i]['offset']['text'] = self.read_config(f'col_{i}','pattern_offset')
        self._columns_heading[i]['offset']['is_include'] = False if self.read_config(f'col_{i}','is_include_offset')=='0' \
            else True


    def set_field_sub(self, fld, name, i:int):
        j = 0
        while self.read_config(f'{name}_{i}_{j}','pattern'):
            fld.append(
                    {
                    'row' : self.read_config(f'{name}_{i}_{j}','row',isNumeric=True),
                    'column' : self.read_config(f'{name}_{i}_{j}','column',isNumeric=True),
                    'pattern' : self.read_config(f'{name}_{i}_{j}','pattern'),
                    'column_offset' : self.read_config(f'{name}_{i}_{j}','column_offset',isNumeric=True),
                    'pattern_offset' : self.read_config(f'{name}_{i}_{j}','pattern_offset'),
                    'func' : self.read_config(f'{name}_{i}_{j}','func'),
                    'func_pattern' : self.read_config(f'{name}_{i}_{j}','func_pattern'),
                    }
            )
            j += 1

    @check_error
    def set_documents(self, k:int) -> NoReturn:
        doc = dict()
        doc['name'] = self.read_config(f'doc_{k}','name')
        doc['fields'] = list()
        num_docs = self.read_config(f'doc_{k}','fields_count',isNumeric=True)
        for i in range(num_docs[0]):
            fld = dict()
            fld['name'] = self.read_config(f'{doc["name"]}_{i}','name') #имя аттрибута
            fld['pattern'] =  self.read_config(f'{doc["name"]}_{i}','pattern') #шаблон поиска (регулярное выражение)
            fld['column'] =  self.read_config(f'{doc["name"]}_{i}','col_config',isNumeric=True) #колонка для поиска данных аттрибут
            fld['row'] =  self.read_config(f'{doc["name"]}_{i}','row_data',isNumeric=True) #запись (в области) для поиска данных атрибутта
            fld['column_offset'] =  self.read_config(f'{doc["name"]}_{i}','col_offset',isNumeric=True) #колонка для поиска данных аттрибут
            fld['pattern_offset'] =  self.read_config(f'{doc["name"]}_{i}','pattern_offset') #шаблон поиска (регулярное выражение)
            fld['func'] =  self.read_config(f'{doc["name"]}_{i}','func') #запись (в области) для поиска данных атрибутта
            fld['func_pattern'] =  self.read_config(f'{doc["name"]}_{i}','func_pattern') #шаблон поиска (регулярное выражение)
            fld['sub'] = []
            doc['fields'].append(fld)

            self.set_field_sub(fld['sub'], doc["name"], i)


        for fld in doc['fields']:
            if fld['pattern'][0:1] == "@":
                fld['pattern'] = doc['fields'][int(fld['pattern'][1:])]['pattern']
        self._documents.append(doc)

    @check_error
    def get_range(self, x:str) -> list:
        return [ int(i) for i in x.split(',')]


    def read_config(self, name_section:str, name_param:str, isNumeric:bool=False):
        try:
            result:str = self._config[name_section][name_param]
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

