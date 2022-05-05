import configparser 
import sys
from report_pu import ReportPU
from gisconfig import GisConfig

if __name__ == "__main__":
    file_name="documents/отчёт по приборам учёта декабрь 2021.xls"
    inn = '0000000000'
    if len (sys.argv) > 1:  file_name = sys.argv[1]
    if len (sys.argv) > 2:  inn = sys.argv[2]

    rep = ReportPU("gisconfig.ini")
    if rep.is_init() and rep.read(filename = file_name, inn = inn):
        print(rep._documents[-1])

