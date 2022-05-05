import configparser
import sys
from report_pu import ReportPU
from gisconfig import GisConfig

if __name__ == "__main__":
    if len (sys.argv) < 2:
        print('run:  <file.xsl>  <inn>')
        exit

    file_name = sys.argv[1]
    inn = sys.argv[2]

    rep = ReportPU("gisconfig.ini")
    if rep.is_init() and rep.read(filename = file_name, inn = inn):
        print(rep._documents[-1])

