from email import utils
import sys
import os
import logging
from module.utils import get_files
from report.report_001_00 import Report_001_00

if __name__ == "__main__":

    list_files, inn = get_files()
    i = 0
    for file_name in list_files:
        i += 1
        if file_name['config']:
            rep = Report_001_00(file_name=file_name['name'],
                                inn=inn, config_file=file_name['config'])
            if rep.read():
                rep.write_collections(i)
                rep.write_logs(i)
        else:
            logging.warning(
                'не найден файл конфигурации для "{}". skip'.format(file_name['name']))
    if not list_files:
        logging.warning('не найден файл "{}". skip'.format(sys.argv[1]))
