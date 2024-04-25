import os
import re
import logging
import shutil
import datetime
import psutil
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
from module.settings import *

logger = logging.getLogger(__name__)


class Parser:
    def __init__(
        self,
        file_name: str = "",
        inn: str = "",
        file_config: str = "",
        union: str = PATH_OUTPUT,
        path_down: str = PATH_OUTPUT,
        file_down: str = "output",
        hash: str = "yes",
        is_daemon: bool = False,
    ) -> None:
        self.logs = list()
        self._dictionary = dict()
        self.name = file_name
        self._period = datetime.date.today().replace(day=1)
        self.inn = inn
        self.config = file_config
        self.union = union
        self.download_path = path_down
        self.output_path = (
            re.findall(".+(?=[.])", file_down)[0]
            if re.findall(".+(?=[.])", file_down)
            else ""
        )
        if not self.output_path:
            self.output_path = inn if inn else "output"
        self.download_file = file_down
        self.is_hash = False if hash == "no" else True
        self.check_tarif = False
        self.is_daemon = is_daemon
        self.config_files = get_config_files()
        self.mem = round(psutil.virtual_memory().available / 1024**3, 2)

    def start(self) -> list:
        try:
            if not self.name:
                if not self.union:
                    logger.warning(
                        "run with parameters:  [--name|-n]=<file.lst>|<file.xsl>|<file.zip> [[--inn|-i]=<inn>] [[--config|-c]=<config.ini>] [[--union|-u]=<path>"
                    )
                else:
                    u = UnionData(
                        path_input=os.path.join(PATH_OUTPUT, self.output_path),
                        path_output=self.download_path,
                        file_output=self.download_file,
                        inn=self.inn,
                    )
                    return u.start()

            else:
                logger.info(
                    f"Архив: {COLOR_CONSOLE['red']}'{os.path.basename(self.name) }'{COLOR_CONSOLE['end']}"
                )
                search_conf = SearchConfig(
                    file_name=self.name,
                    config_files=self.config_files,
                    inn=self.inn,
                    file_conf=self.config,
                    is_daemon=self.is_daemon,
                )
                list_files = search_conf.get_list_files()
                isParser = False
                if list_files:
                    for index, file_name in enumerate(list_files, 1):
                        if file_name["config"] and file_name["config"][0]["sheets"]:
                            rep: ExcelBaseImporter = ExcelBaseImporter(
                                file_name=file_name["name"],
                                inn=file_name["inn"],
                                config_files=file_name["config"],
                                index=index,
                                output=self.output_path,
                                period=self._period,
                                is_hash=self.is_hash,
                                dictionary=self._dictionary.copy(),
                                download_file=(
                                    os.path.join(self.download_path, self.download_file)
                                    if self.is_daemon
                                    else ""
                                ),
                                progress=round(
                                    ((index - 1) / len(list_files)) * 100, 2
                                ),
                            )
                            if (
                                self.check_tarif is False
                                and not rep._dictionary.get("tarif") is None
                            ):
                                self.check_tarif = True
                                mess = check_tarif(rep._dictionary.get("tarif"))
                                if mess:
                                    raise CheckTarifException(mess)
                            free_mem = round(
                                psutil.virtual_memory().available / 1024**3, 2
                            )
                            logger.info(
                                f"({index}/{len(list_files)}) {free_mem}/{self.mem}({round(100*free_mem/self.mem,2)}%) Начало обработки файла '{os.path.basename(file_name['name'])}'"
                            )
                            if rep.extract():
                                logger.info(f"Обработка завершена      ")
                                isParser = True
                                self._dictionary = rep._dictionary.copy()
                                if rep._parameters.get("period"):
                                    self._period = datetime.datetime.strptime(
                                        rep._parameters["period"]["value"][0],
                                        "%d.%m.%Y",
                                    ).date()

                            else:
                                logger.info(f"Неудачное завершение обработки")
                    file_log = write_list(
                        path_output=os.path.join(PATH_LOG, self.output_path),
                        files=list_files,
                    )
                    if self.union:
                        logger.info(f"Сборка документов")
                        u = UnionData(
                            isParser=isParser,
                            file_log=file_log,
                            path_input=os.path.join(PATH_OUTPUT, self.output_path),
                            path_output=self.download_path,
                            file_output=self.download_file,
                            is_daemon=self.is_daemon,
                            inn=self.inn,
                        )
                        result = u.start()
                        logger.info(f"Окончание сборки")
                        return result
                else:
                    logger.info(f"Данные в архиве не распознаны")
                    if self.is_daemon:
                        file_name = os.path.join(self.download_path, self.download_file)
                        write_log_time(file_name, True)
        except InnMismatchException as ex:
            logger.error(f"{ex}")
            return f"{ex}"
        except FatalException as ex:
            logger.error(f"{ex}")
            return f"{ex._message}"
        except ConfigNotFoundException as ex:
            logger.error(f"{ex}")
            return f"{ex._message}"
        except CheckTarifException as ex:
            logger.error(f"{ex}")
            return f"{ex._message}"
        except Exception as ex:
            logger.error(f"{ex}")
            return f"{ex}"
        shutil.copy(
            os.path.join(BASE_DIR, "doc", "error.txt"),
            os.path.join(self.download_path, "error.txt"),
        )
        if not self.is_daemon:
            return "error.txt"
        else:
            file_name = os.path.join(self.download_path, self.download_file)
            write_log_time(file_name, True)

    @staticmethod
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
