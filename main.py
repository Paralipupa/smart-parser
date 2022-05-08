import configparser
import sys
from report.report_001_00 import Report_001_00
from module.gisconfig import GisConfig

if __name__ == "__main__":
    if len (sys.argv) < 4:
        print('run with parameters:  <file.xsl> <inn> <config.ini>')
        exit()

    file_name = sys.argv[1]
    inn = sys.argv[2]
    file_config = sys.argv[3]

    rep = Report_001_00(file_name=file_name, inn=inn, config_file=file_config)
    if rep.read():
        rep.write_collections()

