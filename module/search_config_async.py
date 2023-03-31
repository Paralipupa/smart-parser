import asyncio
from asgiref.sync import sync_to_async
import pathlib
from report.report_001_00 import Report_001_00
from .helpers import (
    print_message,
    get_inn,
    get_list_files,
    get_extract_files,
    timing,
    hashit,
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
        self.headers: dict = dict()
        print_message("", flush=True)

    @timing(
        start_message="Начало поиска конфигурации",
        end_message="Поиск конфигурации завершен",
    )
    def get_list_files(self) -> list:
        self.__extarct_zip_files()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__enumeration_config_files())
        loop.close()
        return self.list_files

    async def __enumeration_config_files(self) -> None:
        tasks = []
        for item in self.list_files:
            tasks.append( asyncio.create_task(self.__put_data_file(item)) )
        l = asyncio.gather(*tasks)
        self.list_files = sorted(
            self.list_files, key=lambda x: (str(x["config"]), str(x["name"]))
        )

    async def __put_data_file(self, item: dict) -> dict:
        data_file: dict = self.__get_data_file(item)
        if item["config"]:
            await self.__check_config(data_file, item["config"])
        else:
            await self.__config_find(data_file)
        return data_file

    def __config_find(self, data_file: dict) -> dict:
        for conf_file in self.config_files:
            if self.__check_config(
                data_file, pathlib.Path(PATH_CONFIG, f"{conf_file}")
            ):
                break

    def __check_config(self, data_file: dict, file_config: str) -> bool:
        rep = Report_001_00(
            file_name=data_file["name"],
            config_file=str(file_config),
            inn=data_file["inn"],
        )
        if rep.is_file_exists:
            if not rep._config._is_unique:
                key = hashit(data_file["name"].encode("utf-8"))
                self.headers.setdefault(key, [])
                if rep.check(self.headers[key]):
                    data_file["config"] = file_config
                    return True
                elif rep._config._warning:
                    for w in rep._config._warning:
                        data_file["warning"].append(w)
                data_file["config"] = ""
        if not rep.is_file_exists:
            data_file["warning"].append(
                'ФАЙЛ НЕ НАЙДЕН или ПОВРЕЖДЕН "{}". skip'.format(data_file["name"])
            )
        return False

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

    def __get_data_file(self, item: dict) -> dict:
        return {
            "name": item["name"],
            "config": item["config"],
            "inn": item["inn"],
            "warning": list(),
            "records": None,
            "zip": item["zip"],
        }
