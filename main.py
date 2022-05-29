from email import utils
import sys
import os
import logging
from module.utils import get_files
from report.report_001_00 import Report_001_00
from report.report_002_00 import Report_002_00
from report.report_003_00 import Report_003_00
from module.gisconfig import regular_calc

report = {
    '001': Report_001_00,
    '002': Report_002_00,
    '003': Report_003_00
}
if __name__ == "__main__":

    path = 'output'
    list( map( os.unlink, (os.path.join( path,f) for f in os.listdir(path)) ) )
    path = 'logs'
    list( map( os.unlink, (os.path.join( path,f) for f in os.listdir(path)) ) )


    list_files, inn, warning = get_files()
    i = 0
    for file_name in list_files:
        i += 1
        if file_name['config']:
            t = regular_calc('[0-9]{3}(?=_)', file_name['config'])
            rep = report[t](file_name=file_name['name'],
                                inn=inn, config_file=file_name['config'])
            if rep.read():
                rep.write_collections(i)
                rep.write_logs(i)
        else:
            s = ' '.join([x for x in warning]).strip()
            if s:
                logging.warning(s)
            else:
                logging.warning(
                    'не найден файл конфигурации для "{}". skip'.format(file_name['name']))
    if not list_files:
        logging.warning('не найден файл "{}". skip'.format(sys.argv[1]))
