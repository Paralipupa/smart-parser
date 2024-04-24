import pathlib, logging, re, json
from multiprocessing import Manager
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.managers import ListProxy, DictProxy
from typing import List
from time import sleep
from .excel_base_importer import ExcelBaseImporter
from .helpers import (
    print_message,
    get_inn,
    get_list_files,
    get_extract_files,
    get_data_file,
    fatal_error,
    hashit,
)
from .settings import *

logger = logging.getLogger(__name__)
manager = Manager()
man_list: ListProxy = manager.list()
man_dict: DictProxy = manager.dict()
man_dict.headers = dict()


class SearchConfig:
    def __init__(
        self,
        file_name: str,
        config_files: list,
        inn: str = "",
        file_conf: str = "",
        is_daemon: bool = False,
    ):
        self.file_name = file_name
        self.inn = inn if inn else get_inn(file_name)
        self.file_conf = file_conf
        self.config_files = config_files.copy()
        self.list_files = []
        self.zip_files = []
        self.headers: dict = dict()
        self.counter: int = 0
        self.is_daemon = is_daemon
        print_message("", flush=True)

    @fatal_error
    def get_list_files(self) -> list:
        data_alignment = self.checking_configuration()
        self.__extact_zip_files()
        self.__enumeration_config_files()
        self.write_configuration(data_alignment)
        clear_manager()
        return self.list_files

    def __enumeration_config_files(self) -> None:
        if len(self.list_files) == 0:
            return
        clear_manager()
        # with ThreadPoolExecutor(max_workers=None) as executor:
        #     executor.map(self.put_data_file, self.list_files)
        d = list(map(self.put_data_file, self.list_files))
        self.__to_collect_out_files()
        return

    def put_data_file(self, data_file: dict) -> dict:
        if data_file["config"][-1]["name"] == "":
            self.__config_find(data_file)
        else:
            self.__check_config(data_file)
        sleep(0)
        return data_file

    def __config_find(self, data_file: dict) -> dict:
        retrieved = set()
        try:
            if len(self.config_files) == 1:
                data_file["config"][-1]["name"] = pathlib.Path(
                    PATH_CONFIG, f"{self.config_files[0]['name']}"
                )
                data_file["config"][-1]["sheets"].append(-1)
                man_list.append(data_file)
            else:
                for conf_file in self.config_files:
                    if not conf_file["type"] in retrieved:
                        data_file["config"][-1]["name"] = pathlib.Path(
                            PATH_CONFIG, f"{conf_file['name']}"
                        )
                        if self.__check_config(data_file):
                            retrieved.add(conf_file["type"])
        except Exception as ex:
            logger.info(
                f"error  {conf_file['name']} \t {os.path.basename(data_file['name'])}  ${ex}"
            )
            logger.exception("config_find")

    def __check_config(self, data_file: dict) -> bool:
        rep: ExcelBaseImporter = ExcelBaseImporter(
            file_name=data_file["name"],
            config_files=data_file["config"],
            inn=data_file["inn"],
        )
        if rep.is_file_exists:
            key = hashit(data_file["name"].encode("utf-8"))
            man_dict.headers.setdefault(key, [])
            b = rep.check(man_dict.headers[key])
            man_list.append(data_file)
            return b
        if not rep.is_file_exists:
            data_file["config"]["warning"].append(
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
                get_data_file(
                    {
                        "name": self.file_name,
                        "config": self.file_conf,
                        "inn": self.inn,
                        "zip": "",
                    }
                )
            )

        if self.zip_files:
            for file_name in self.zip_files:
                file_name["inn"] = self.inn
                file_name["config"] = [self.file_conf]
                file_conf = get_extract_files(archive_file=file_name)
                self.list_files.extend(file_conf)
        return

    def __to_collect_out_files(self) -> None:
        manage_list = get_manager_list()
        manage_dict = dict()
        for l in manage_list:
            if len(l["config"][0]["sheets"]) != 0:
                manage_dict.setdefault(l["name"], get_data_file())
                manage_dict[l["name"]]["config"] = l["config"]
                manage_dict[l["name"]]["name"] = l["name"]
                manage_dict[l["name"]]["inn"] = l["inn"]
            else:
                if manage_dict.get(l["name"]) is None:
                    manage_dict.setdefault(l["name"], get_data_file())
                    manage_dict[l["name"]]["config"][0]["warning"].extend(
                        l["config"][0]["warning"]
                    )
                    manage_dict[l["name"]]["name"] = l["name"]
                    manage_dict[l["name"]]["inn"] = l["inn"]

        list_data_file = []
        for l in manage_dict.values():
            list_data_file.append(l)

        # сортируем сначала найденые конфигурации
        # сортируем сначала конфигурация 000_00 (словари)
        if list_data_file:
            for data_file in list_data_file:
                data_file["config"] = sorted(
                    data_file["config"],
                    key=lambda x: (
                        (
                            0
                            if str(x["name"]).find("000") != -1
                            else (1 if str(x["name"]).find("002") != -1 else 2)
                        ),
                        x["sheets"],
                    ),
                )
            self.list_files = sorted(
                list_data_file,
                key=lambda x: (
                    (
                        0
                        if str(x["config"][0]["name"]).find("000") != -1
                        else (1 if str(x["config"][0]["name"]).find("002") != -1 else 2)
                    ),
                    str(x["name"]),
                ),
            )
        else:
            self.list_files = []
        return

    def checking_configuration(self) -> dict:
        """Проверка соответствия файлов конфигурации по ИНН"""
        data = dict()
        if pathlib.Path.exists(pathlib.Path(CONFIGURATION_FILE)):
            with open(
                pathlib.Path(CONFIGURATION_FILE), mode="r", encoding=ENCONING
            ) as file:
                data = json.load(file)
            if self.inn != "000000000" and data.get(self.inn):
                self.config_files = [
                    x for x in self.config_files if x["name"] in data[self.inn]
                ]
        return data

    def write_configuration(self, data: dict):
        """Запись соответствия файлов конфигурации по ИНН"""
        for item in self.list_files:
            if item["inn"] and item["inn"] != "0000000000":
                data.setdefault(item["inn"], [])
                for conf in item["config"]:
                    name = os.path.basename(conf["name"])
                    if bool(data) is False or not name in data[item["inn"]]:
                        data[item["inn"]].append(name)
        with open(
            pathlib.Path(CONFIGURATION_FILE), mode="w", encoding=ENCONING
        ) as file:
            jstr = json.dumps(data, indent=4, ensure_ascii=False)
            file.write(jstr)


def clear_manager():
    man_dict.headers.clear()
    for _ in range(len(man_list)):
        man_list.pop()


def get_manager_list() -> list:
    l = []
    for _ in range(len(man_list)):
        l.append(man_list.pop())
    return l
