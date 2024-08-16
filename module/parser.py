import os
import re
import logging
import shutil
import datetime
import psutil
from functools import partial
from time import time, gmtime, strftime, sleep
from pathlib import Path
from module.excel_base_importer import ExcelBaseImporter
from module.helpers import get_config_files, write_list, check_tarif, write_log_time
from module.union import UnionData
from module.exceptions import (
    InnMismatchException,
    FatalException,
    ConfigNotFoundException,
    CheckTarifException,
)
from module.search_config_tasks import SearchConfig
from module.utils import make_archive
from module.settings import *

from multiprocessing import Process, Pool, Manager, Lock, Value, Queue, Semaphore
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


logger = logging.getLogger(__name__)

man_list = Manager().list()
man_dict = Manager().dict()
man_dict["name"] = ""
man_dict["result"] = ""
man_dict["period"] = ""
lock = Lock()


class Parser:
    def __init__(
        self,
        file_name: str = "",
        inn: str = "",
        file_config: str = "",
        union: str = PATH_OUTPUT,
        path_down: str = PATH_DOWNLOAD,
        file_down: str = "output",
        hash: str = "yes",
        is_daemon: bool = False,
    ) -> None:
        self.logs = list()
        self.name = file_name
        self._period = datetime.date.today().replace(day=1)
        self.inn = inn
        self.config = file_config
        self.union = union
        self.download_path = path_down
        self.output_path = os.path.basename(
            re.findall(".+(?=[.])", file_down)[0]
            if re.findall(".+(?=[.])", file_down)
            else ""
        )
        if not self.output_path:
            self.output_path = inn if inn else "output"
        self.is_hash = False if hash == "no" else True
        self.check_tarif = False
        self.is_daemon = is_daemon
        self.config_files = get_config_files()
        self.mem = round(psutil.virtual_memory().available / 1024**3, 2)
        self.list_files = None
        self.isParser = False
        self.file_log = ""
        self.count = 0
        self.download_file = self.get_file_output(file_down)
        self.clear_manager()
        self._dictionary = dict()

    def start(self) -> list:
        try:
            self.set_period(self._period)
            self.set_download_file(self.download_file)
            self.set_result(self.get_download_file())
            nstart = time()
            if not self.name:
                self.final_union(nstart)
            else:
                logger.info(
                    f"Архив: {COLOR_CONSOLE['red']}'"
                    + f"{re.findall('.+(?=_20)',os.path.basename(self.name))[0] if re.findall('.+(?=_20)',os.path.basename(self.name)) else os.path.basename(self.name) }"
                    + f"'{COLOR_CONSOLE['end']}"
                )
                self.run_background(nstart)
        except (ConfigNotFoundException, CheckTarifException) as ex:
            logger.error(f"{ex}")
            self.set_result(f"{ex._message}")
        except FatalException as ex:
            logger.error(f"{ex}")
            self.set_result(f"{ex._message}")
        except (InnMismatchException, Exception) as ex:
            logger.error(f"{ex}")
            self.set_result(f"{ex}")
        return self.get_result()

    def run_background(self, nstart):
        main_process = Process(
            target=self.manage_tasks, args=(nstart,), name="smart-parser"
        )
        main_process.start()
        if self.is_daemon:
            main_process.join(0)
        else:
            main_process.join()
            if main_process.exitcode != 0:
                self.set_result(
                    f"Процесс {main_process.pid} завершился с ошибкой. Код завершения: {main_process.exitcode}"
                )
        return

    def process_run(self, data):
        self.stage_extract(data[0], data[1])

    def manage_tasks(self, nstart):
        self.set_result(None)
        self.list_files = self.get_config()
        if self.list_files:
            try:
                self.count = len(self.list_files)
                parsers_0 = self.get_processes("_000_")
                parsers_1 = self.get_processes("_001_")
                parsers_2 = self.get_processes("_002_")
                _ = list(map(self.process_run, parsers_0))
                _ = list(map(self.process_run, parsers_1))
                _ = list(map(self.process_run, parsers_2))
                # with ProcessPoolExecutor(max_workers=4) as executor:
                #     executor.map(self.process_run, parsers_2)
                self.stage_finish(nstart)
            except Exception as ex:
                file_name = os.path.join(self.download_path, self.get_download_file())
                make_archive(file_name, **dict(error=f"{ex}"))
                if self.is_daemon:
                    write_log_time(file_name, True)
        if not self.get_result():
            logger.info(
                f"Данные в архиве не распознаны {strftime('%H:%M:%S', gmtime(time()-nstart))}"
            )
            file_name = os.path.join(self.download_path, self.get_download_file())
            make_archive(file_name, **dict(error="Данные в архиве не распознаны"))
            if self.is_daemon:
                write_log_time(file_name, True)
            self.set_result(self.get_download_file())
        return

    def get_processes(self, pattern: str) -> list:
        return [
            (name, index)
            for index, name in enumerate(self.list_files, 1)
            if pattern in str(name["config"][0]["name"])
        ]

    def stage_finish(self, nstart):
        self.file_log = write_list(
            path_output=os.path.join(PATH_LOG, self.output_path),
            files=self.list_files,
        )
        self.final_union(nstart)
        return

    def stage_extract(self, file_name: dict, counter: int):
        if file_name["config"] and file_name["config"][0]["sheets"]:
            dictionary = self.get_dictionary_manager()
            rep: ExcelBaseImporter = ExcelBaseImporter(
                file_name=file_name["name"],
                inn=file_name["inn"],
                config_files=file_name["config"],
                index=counter,
                output=self.output_path,
                period=self.get_period(),
                is_hash=self.is_hash,
                dictionary=dictionary,
                download_file=(
                    os.path.join(self.download_path, self.get_download_file())
                    if self.is_daemon
                    else ""
                ),
                count=self.count,
            )
            if self.check_tarif is False and not rep._dictionary.get("tarif") is None:
                self.check_tarif = True
                mess = check_tarif(rep._dictionary.get("tarif"))
                if mess:
                    raise CheckTarifException(mess)
            free_mem = round(psutil.virtual_memory().available / 1024**3, 2)
            logger.info(
                f"({counter}/{self.count}) (dict={len(self._dictionary)}) {free_mem}/{self.mem}({round(100*free_mem/self.mem,2)}%) "
                + f"Начало обработки файла '{os.path.basename(file_name['name'])}'({Path(file_name['config'][0]['name']).stem})"
            )
            inn = rep.extract()
            if inn:
                self.inn = inn
                if not self.is_daemon:
                    self.set_download_file(
                        self.get_file_output(self.get_download_file())
                    )
                    self.set_result(self.get_download_file())
                logger.info(f"Обработка завершена      ")
                self.set_dictionary_manager(rep._dictionary)
                self.isParser = True
                if rep._parameters.get("period"):
                    d = datetime.datetime.strptime(
                        rep._parameters["period"]["value"][0],
                        "%d.%m.%Y",
                    ).date()
                    if self.get_period() > d:
                        self.set_period(d)

            else:
                logger.info(f"Неудачное завершение обработки")

    def get_config(self):
        search_conf = SearchConfig(
            file_name=self.name,
            config_files=self.config_files,
            inn=self.inn,
            file_conf=self.config,
            is_daemon=self.is_daemon,
        )
        list_files = search_conf.get_list_files()
        return list_files

    def final_union(self, nstart):
        result = ""
        if self.union:
            logger.info(f"Сборка документов")
            u = UnionData(
                isParser=self.isParser,
                file_log=self.file_log,
                path_input=os.path.join(PATH_OUTPUT, self.output_path),
                path_output=self.download_path,
                file_output=self.get_download_file(),
                is_daemon=self.is_daemon,
                inn=self.inn,
            )
            result = u.start()
            logger.info(
                f"Окончание сборки {strftime('%H:%M:%S', gmtime(time()-nstart))} {'. Архив не сформирован' if bool(result) is False else ''}"
            )
            self.set_result(result)
        return

    def download(self):
        if not self.union:
            logger.warning(
                "run with parameters:  [--name|-n]=<file.lst>|<file.xsl>|<file.zip> [[--inn|-i]=<inn>] [[--config|-c]=<config.ini>] [[--union|-u]=<path>"
            )
        else:
            u = UnionData(
                path_input=os.path.join(PATH_OUTPUT, self.output_path),
                path_output=self.download_path,
                file_output=self.get_download_file(),
                inn=self.inn,
            )
            return u.start()

    def get_file_output(self, file_name) -> str:
        return (
            file_name
            if file_name
            and (
                not file_name.startswith("output")
                or (self.inn and self.inn.startswith("0000"))
            )
            else (
                (
                    f'{self.inn if self.inn else "output"}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.zip'
                )
            )
        )

    def set_result(self, val):
        man_dict["result"] = val

    def get_result(self):
        return man_dict["result"]

    def set_download_file(self, val):
        man_dict["name"] = val

    def get_download_file(self):
        return man_dict["name"]

    def set_period(self, val):
        man_dict["period"] = val

    def get_period(self):
        return man_dict["period"]

    def set_dictionary_manager(self, d: list):
        # with lock:
        #     if d:
        #         for key, value in d.items():
        #             man_list.append((key, value))
        self._dictionary = d

    def get_dictionary_manager(self) -> list:
        # d: dict = dict()
        # with lock:
        #     for i in range(len(man_list)):
        #         x = man_list[i]
        #         d[x[0]] = x[1]
        # return d
        return self._dictionary

    def clear_manager(self):
        del man_list[:]


def get_path(pathname: str) -> str:
    if pathname == "logs":
        return PATH_LOG
    elif pathname == "output":
        return PATH_OUTPUT
    elif pathname == "tmp":
        return PATH_TMP
    else:
        if pathname.find("log") != -1 and os.path.exists(
            os.path.join(BASE_DIR, pathname)
        ):
            return os.path.join(BASE_DIR, pathname)
    return ""
