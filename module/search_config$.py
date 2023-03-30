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

    @timing(
        start_message="Начало поиска конфигурации",
        end_message="Поиск конфигурации завершен",
    )
    def get_list_files(self) -> list:
        self.__extarct_zip_files()
        asyncio.run(self.__enumeration_config_files())
        return self.list_files

    async def __enumeration_config_files(self) -> None:
        q = asyncio.Queue()
        put_files = [
            asyncio.create_task(self.__put_data_file(item, q))
            for item in self.list_files
        ]
        get_files = [asyncio.create_task(self.__get_data_file(q))]

        self.list_files = []
        await asyncio.gather(*put_files)
        await q.join()

        for c in get_files:
            c.cancel()

    async def __get_data_file(self, q: asyncio.Queue) -> None:
        while True:
            data_file = await q.get()
            self.list_files.append(data_file)
            q.task_done()

    async def __put_data_file(self, item: dict, q: asyncio.Queue) -> dict:
        data_file = {
            "name": item["name"],
            "config": item["config"],
            "inn": item["inn"],
            "warning": list(),
            "records": None,
            "zip": item["zip"],
        }
        if item["config"]:
            await self.__check_config(data_file, item["config"], q)
        else:
            await self.__config_find(data_file, q)

    # await q.put(data_file)

    async def __config_find(self, data_file: dict, q: asyncio.Queue) -> dict:
        for conf_file in self.config_files:
            b = await self.__check_config(
                data_file, pathlib.Path(PATH_CONFIG, f"{conf_file}"), q
            )
            if b:
                return

    async def __check_config(
        self, data_file: dict, file_config: str, q: asyncio.Queue
    ) -> bool:
        await asyncio.sleep(0)
        rep = Report_001_00(
            file_name=data_file["name"],
            config_file=str(file_config),
            inn=data_file["inn"],
        )
        if rep.is_file_exists:
            if not rep._config._is_unique:
                if rep.check():
                    data_file["config"] = file_config
                    return data_file
                elif rep._config._warning:
                    for w in rep._config._warning:
                        data_file["warning"].append(w)
                data_file["config"] = ""
        if not rep.is_file_exists:
            data_file["warning"].append(
                'ФАЙЛ НЕ НАЙДЕН или ПОВРЕЖДЕН "{}". skip'.format(data_file["name"])
            )
        if data_file["config"]:
            q.put(data_file)
            return True
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
