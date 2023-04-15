import pathlib, logging, re
from multiprocessing import Pool, Manager
from typing import List
from .excel_base_importer import ExcelBaseImporter
from .helpers import (
    print_message,
    get_inn,
    get_list_files,
    get_extract_files,
    timing,
    hashit,
)
from .settings import *

logger = logging.getLogger(__name__)
manager = Manager()
man_list = manager.list()


class SearchConfig:
    def __init__(
        self, file_name: str, config_files: list, inn: str = "", file_conf: str = ""
    ):
        self.file_name = file_name
        self.inn = inn if inn else get_inn(file_name)
        self.file_conf = file_conf
        self.config_files = config_files
        self.list_files = []
        self.zip_files = []
        self.headers: dict = dict()
        self.counter: int = 0
        print_message("", flush=True)

    @timing(
        start_message="Начало поиска конфигурации",
        end_message="Поиск конфигурации завершен",
    )
    def get_list_files(self) -> list:
        self.__extact_zip_files()
        self.__enumeration_config_files()
        return self.list_files

    def __enumeration_config_files(self) -> None:
        if self.list_files == []:
            return
        clear_manager()
        pool = Pool()
        for item in self.list_files:
            pool.apply_async(self.put_data_file, args=(item,))
        pool.close()
        pool.join()
        list_data_file = get_manager_list()
        if list_data_file:
            for data_file in list_data_file:
                data_file["config"] = sorted(
                    data_file["config"], key=lambda x: (x["name"], x["sheets"])
                )
            self.list_files = sorted(
                list_data_file, key=lambda x: (x["config"][0]["name"], x["name"])
            )
        else:
            self.list_files = []
        return

    def put_data_file(self, item: dict) -> dict:
        data_file = self.__get_data_file(item)
        if item["config"] == "":
            self.__config_find(data_file)
        else:
            self.__check_config(data_file)
        return data_file

    def __config_find(self, data_file: dict) -> dict:
        retrieved = set()
        try:
            for conf_file in self.config_files:
                if not conf_file["type"] in retrieved and self.__check_config(
                    data_file,
                    config_name=pathlib.Path(PATH_CONFIG, f"{conf_file['name']}"),
                ):
                    retrieved.add(conf_file["type"])
        except Exception as ex:
            logger.exception("config_find")

    def __check_config(self, data_file: dict, config_name: str = None) -> bool:
        if config_name is None:
            config_file: dict = data_file["config"]
        else:
            config_file: dict = [{"name": config_name, "sheets": []}]
        rep: ExcelBaseImporter = ExcelBaseImporter(
            file_name=data_file["name"],
            config_files=config_file,
            inn=data_file["inn"],
        )
        if rep.is_file_exists:
            key = hashit(data_file["name"].encode("utf-8"))
            self.headers.setdefault(key, [])
            sheets: List[int] = rep.check(self.headers[key])
            if len(sheets) != 0:
                if config_name is None:
                    data_file["config"][-1]["sheets"] = sheets
                else:
                    config_file[0]["sheets"] = sheets
                    data_file["config"].append(config_file[0])
                man_list.append(data_file)
                return True
            elif rep._config._warning:
                for w in rep._config._warning:
                    data_file["warning"].append(w)
        if not rep.is_file_exists:
            data_file["warning"].append(
                'ФАЙЛ НЕ НАЙДЕН или ПОВРЕЖДЕН "{}". skip'.format(data_file["name"])
            )
        return False

    def __extact_zip_files(self) -> None:
        if self.file_name.find(".lst") != -1:
            self.zip_files = get_list_files(self.file_name)
        elif self.file_name.lower().find(".zip") != -1:
            self.zip_files.append(
                {"file": self.file_name, "inn": self.inn, "config": self.file_conf}
            )
        elif self.file_name.lower().find(".xls") != -1:
            self.list_files.append(
                {
                    "name": self.file_name,
                    "config": self.file_conf,
                    "inn": self.inn,
                    "warning": list(),
                    "zip": "",
                }
            )

        if self.zip_files:
            for file_name in self.zip_files:
                file_name["inn"] = self.inn
                file_name["config"] = [self.file_conf]
                file_conf = get_extract_files(archive_file=file_name)
                self.list_files.extend(file_conf)
        return

    def __get_data_file(self, item: dict) -> dict:
        return {
            "name": item["name"],
            "config": [{"name": item["config"], "sheets": []}]
            if item["config"] != ""
            else [],
            "inn": item["inn"],
            "warning": list(),
            "records": None,
            "zip": item["zip"],
        }


def clear_manager():
    for _ in range(len(man_list)):
        man_list.pop()


def get_manager_list() -> list:
    l = []
    for _ in range(len(man_list)):
        l.append(man_list.pop())
    return l
