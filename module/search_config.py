import asyncio
import pathlib
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from report.report_001_00 import Report_001_00
from .helpers import (
    print_message,
    get_inn,
    get_list_files,
    get_extract_files,
    timing,
)
from .settings import *


class SearchConfig:
    def __init__(
        self, file_name: str, config_files: list, inn: str = "", file_conf: str = ""
    ):
        self.file_name = file_name
        self.inn = inn if inn else get_inn(file_name)
        self.file_conf = file_conf
        self.config_files = config_files
        self.list_files = list()
        self.zip_files = list()
        print_message("", flush=True)

    @timing(start_message="Начало поиска конфигурации", end_message="Поиск конфигурации завершен")
    def get_list_files(self) -> list:
        self.__extarct_zip_files()
        self.__enumeration_config_files()
        return self.list_files

    def __extarct_zip_files(self) -> None:
        if self.file_name.find(".lst") != -1:
            self.zip_files = get_list_files(self.file_name)
        elif self.file_name.lower().find(".zip") != -1:
            self.zip_files.append(
                {"file": self.file_name, "inn": self.inn, "config": self.file_conf}
            )
        if self.zip_files:
            for file_name in self.zip_files:
                file_name["inn"] = self.inn
                file_name["config"] = [self.file_conf]
                file_conf = get_extract_files(archive_file=file_name)
                self.list_files.extend(file_conf)
        else:
            self.list_files.append(
                {
                    "name": self.file_name,
                    "config": self.file_conf,
                    "inn": self.inn,
                    "warning": list(),
                    "zip": "",
                }
            )

    def __enumeration_config_files(self) -> None:
        ls_new = list()
        ls_old = self.list_files.copy()
        loop = asyncio.get_event_loop()
        for i, item in enumerate(ls_old, 1):
            asyncio.ensure_future(self.__get_data_file(item, i)) 
        loop.run_forever()
        self.list_files = sorted(
            ls_new, key=lambda x: (str(x["config"]), str(x["name"]))
        )

    # def __enumeration_config_files(self) -> None:
    #     ls_new = list()
    #     ls_old = self.list_files.copy()
    #     for i, item in enumerate(ls_old, 1):
    #         ls_new.append(self.__get_data_file(item, i))
    #     self.list_files = sorted(
    #         ls_new, key=lambda x: (str(x["config"]), str(x["name"]))
    #     )

    # @timing(start_message="Начало", end_message="Завершено")
    # def __enumeration_config_files(self) -> None:
    #     ls_new = self.list_files.copy()
    #     self.list_files = list()
    #     # pool = Pool(4)
    #     # for i, item in enumerate(ls_new):
    #     # ls_new.append(self.__get_data_file(item, i))
    #     # pool.apply_async(self.__get_data_file, args=(item, i,), callback=self.__check_result)
    #     pool = ThreadPool()
    #     pool.map(self.__get_data_file, ls_new)
    #     pool.close()
    #     pool.join()
    #     self.list_files = sorted(
    #         self.list_files.copy(), key=lambda x: (str(x["config"]), str(x["name"]))
    #     )

    async def __get_data_file(self, item: dict, i: int = 0) -> dict:
        data_file = {
            "name": item["name"],
            "config": item["config"],
            "inn": item["inn"],
            "warning": list(),
            "records": None,
            "zip": item["zip"],
        }
        if item["config"]:
            data_file = await self.__check_config(data_file, item["config"])
        else:
            data_file = await self.__config_find(data_file, i)
        return data_file

    def __config_find(self, data_file: dict, j: int = 0) -> dict:
        for i, conf_file in enumerate(self.config_files):
            print_message(
                "          Поиск конфигураций: {}%   \r".format(
                    round(
                        (j * len(self.config_files) + i)
                        / (len(self.list_files) * len(self.config_files))
                        * 100,
                        0,
                    )
                ),
                end="",
                flush=True,
            )
            data_file = self.__check_config(
                data_file, pathlib.Path(PATH_CONFIG, f"{conf_file}")
            )
            if data_file["config"]:
                break
        return data_file

    def __check_config(self, data_file: dict, file_config: str) -> dict:
        # rep = Report_001_00(
        #     file_name=data_file["name"],
        #     config_file=str(file_config),
        #     inn=data_file["inn"],
        # )
        # if rep.is_file_exists:
        #     if not rep._config._is_unique:
        #         if rep.check():
        #             data_file["config"] = file_config
        #             return data_file
        #         elif rep._config._warning:
        #             for w in rep._config._warning:
        #                 data_file["warning"].append(w)
        #         data_file["config"] = ""
        # if not rep.is_file_exists:
        #     data_file["warning"].append(
        #         'ФАЙЛ НЕ НАЙДЕН или ПОВРЕЖДЕН "{}". skip'.format(data_file["name"])
        #     )
        return data_file
