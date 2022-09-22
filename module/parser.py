import sys
import os
import logging
import datetime
from report.report_001_00 import Report_001_00
from report.report_002_00 import Report_002_00
from report.report_003_00 import Report_003_00
from .utils import get_files, write_list, getArgs
from .excel_base_importer import ExcelBaseImporter
from .gisconfig import regular_calc, PATH_OUTPUT, PATH_LOG
from .union import UnionData
from .settings import *

class Parser:

    def __init__(self, file_name: str = '', inn: str = '', file_config: str = '', union: str = PATH_OUTPUT, path_down: str = PATH_OUTPUT) -> None:
        self.logs = list()
        self.name = file_name
        self.inn = inn
        self.config = file_config
        self.union = union
        self.download = path_down
        self.report = {
            '001': Report_001_00,
            '002': Report_002_00,
            '003': Report_003_00
        }

    def start(self) -> list:
        if not self.name:
            if not self.union:
                logging.warning(
                    'run with parameters:  [--name|-n]=<file.lst>|<file.xsl>|<file.zip> [[--inn|-i]=<inn>] [[--config|-c]=<config.ini>] [[--union|-u]=<path>')
            else:
                u = UnionData()
                return u.start(self.union, self.download)
        else:
            list_files = get_files(self.name, self.inn, self.config)
            i = 0
            if list_files:
                for file_name in list_files:
                    i += 1
                    if file_name['config']:
                        if file_name['config'] != '000':
                            t = regular_calc(
                                '[0-9]{3}(?=_)', str(file_name['config']))
                            rep: ExcelBaseImporter = self.report[t](file_name=file_name['name'],
                                                                    inn=file_name['inn'], config_file=str(file_name['config']))
                            if rep.read():
                                rep.write_collections(i)
                                rep.write_logs(i)
                            else:
                                if rep._config._warning:
                                    logging.warning(
                                        f"{file_name['inn']} - {file_name['name']}  не все поля найдены см.logs/")
                            file_name['warning'] += rep._config._warning
                    else:
                        if len(file_name['warning']) != 0:
                            logging.warning(
                                f"{file_name['inn']} - {file_name['name']}")
                        else:
                            logging.warning(
                                f"{file_name['inn']} - {file_name['name']} не найден файл конфигурации.")
                write_list(list_files)
                if self.union:
                    u = UnionData()
                    return u.start(self.union, self.download)
        return ''

    @staticmethod
    def get_path(pathname:str)->str:
        if pathname == 'log':
            return PATH_LOG
        elif pathname == 'output':
            return PATH_OUTPUT
        elif pathname == 'tmp':
            return PATH_TMP
        return ''

