import sys, os, logging
from report.report_001_00 import Report_001_00

if __name__ == "__main__":
    if len (sys.argv) < 3:
        print('run with parameters:  <file.xsl> <inn> [<config.ini>]')
        exit()

    file_name = sys.argv[1]
    inn = sys.argv[2]
    if len (sys.argv) >= 4:
        file_config = sys.argv[3]
    else:
        path = 'config'
        files = os.listdir(path)
        file_config = ''
        for file in files:
            file_config = f'{path}/{file}'
            rep = Report_001_00(file_name=file_name, inn=inn, config_file=file_config)
            if rep.check(is_warning=False):
                break
            file_config = ''

    if file_config:
        rep = Report_001_00(file_name=file_name, inn=inn, config_file=file_config)
        if rep.read():
            rep.write_collections()
    else:
        logging.warning('не найден файл конфигурации для "{}". skip'.format(file_name))

