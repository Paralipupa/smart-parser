import os
import re
import logging
import shutil
import datetime
from .excel_base_importer import ExcelBaseImporter
from .helpers import get_config_files, write_list, check_tarif
from .union import UnionData
from .exceptions import (
    InnMismatchException,
    FatalException,
    ConfigNotFoundException,
    CheckTarifException,
)
from .search_config_tasks import SearchConfig
from .settings import *

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
    ) -> None:
        self.logs = list()
        self._dictionary = dict()
        self.name = file_name
        self._period = datetime.date.today().replace(day=1)
        self.inn = inn
        self.config = file_config
        self.union = union
        self.download_path = path_down
        self.output_path = re.findall(".+(?=[.])", file_down)[0]
        self.download_file = file_down
        self.is_hash = False if hash == "no" else True
        self.check_tarif = False
        self.config_files = get_config_files()

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
                    )
                    return u.start()

            else:
                logger.info(
                    f"Архив: {COLOR_CONSOLE['red']}'{os.path.basename(self.name) }'{COLOR_CONSOLE['end']}"
                )
                search_conf = SearchConfig(
                    self.name, self.config_files, self.inn, self.config
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
                            )
                            rep.is_hash = self.is_hash
                            rep._dictionary = self._dictionary.copy()
                            if (
                                self.check_tarif is False
                                and not rep._dictionary.get("tarif") is None
                            ):
                                self.check_tarif = True
                                mess = check_tarif(rep._dictionary.get("tarif"))
                                if mess:
                                    raise CheckTarifException(mess)
                            logger.info(
                                f"Начало обработки файла '{os.path.basename(file_name['name'])}'"
                            )
                            if rep.extract():
                                logger.info(f"Обработка завершена")
                                isParser = True
                                self._dictionary = rep._dictionary.copy()
                                self._period = datetime.datetime.strptime(
                                    rep._parameters["period"]["value"][0], "%d.%m.%Y"
                                ).date()

                            else:
                                logger.info(f"Неудачное завершение обработки")
                    file_log = write_list(
                        path_output=os.path.join(PATH_LOG, self.output_path),
                        files=list_files,
                    )
                    if self.union:
                        u = UnionData(
                            isParser=isParser,
                            file_log=file_log,
                            path_input=os.path.join(PATH_OUTPUT, self.output_path),
                            path_output=self.download_path,
                            file_output=self.download_file,
                        )
                        return u.start()
                else:
                    logger.info(f"Данные в архиве не распознаны")
        except InnMismatchException as ex:
            return f"{ex}"
        except FatalException as ex:
            return f"{ex._message}"
        except ConfigNotFoundException as ex:
            return f"{ex._message}"
        except CheckTarifException as ex:
            return f"{ex._message}"
        except Exception as ex:
            logger.exception("Error start")
            return f"{ex}"
        shutil.copy(
            os.path.join(BASE_DIR, "doc", "error.txt"),
            os.path.join(self.download_path, "error.txt"),
        )
        return "error.txt"

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
