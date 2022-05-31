from email import utils
import sys
import os
import logging
from module.utils import get_files, write_list
from report.report_001_00 import Report_001_00
from report.report_002_00 import Report_002_00
from report.report_003_00 import Report_003_00
from module.gisconfig import regular_calc, PATH_OUTPUT, PATH_LOG

report = {
    '001': Report_001_00,
    '002': Report_002_00,
    '003': Report_003_00
}
if __name__ == "__main__":

    if os.path.isdir(PATH_OUTPUT):
        list( map( os.unlink, (os.path.join(PATH_OUTPUT,f) for f in os.listdir(PATH_OUTPUT)) ) )
    if os.path.isdir(PATH_LOG):
        list( map( os.unlink, (os.path.join(PATH_LOG,f) for f in os.listdir(PATH_LOG)) ) )

    list_files = get_files()
    i = 0
    if list_files:
        for file_name in list_files:
            i += 1
            if file_name['config']:
                t = regular_calc('[0-9]{3}(?=_)', str(file_name['config']))
                rep = report[t](file_name=file_name['name'],
                                    inn=file_name['inn'], config_file=str(file_name['config']))
                if rep.read():
                    rep.write_collections(i)
                    rep.write_logs(i)
                else:
                    if rep._config._warning:
                        print('error')
                file_name['warning'] += rep._config._warning
            else:
                s = ' '.join([x for x in file_name['warning']]).strip()
                if s:
                    logging.warning(s)
        write_list(list_files)
