import configparser 

from report_pu import ReportPU
FILE_NAME="documents/отчёт по приборам учёта декабрь 2021.xls"
if __name__ == "__main__":
    config = configparser.ConfigParser()  
    config.read("settings.ini")  
    rep = ReportPU()
    rep.set_condition_range(config["Отчет по ИПУ"]["condition_range"])
    rep.set_columns_def(config["Отчет по ИПУ"]["columns_def"].split('|'))
    if rep.read(filename = FILE_NAME, inn = "000000000"):
        print(rep._documents[0])

