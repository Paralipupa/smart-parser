import os, re
import shutil
import sys
from module.helpers import timing

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path)
from module.settings import ENCONING
from module.settings import BASE_DIR
from module.parser import Parser
from module.utils import get_extract_files
import unittest
from shutil import rmtree

IS_HASH = False

class TestGisConfig(unittest.TestCase):
    def __diff(self, path_new: str, path_old: str, files: list) -> list:
        miss_lines = list()
        files_new = []
        for f in files:
            miss_lines.append({"name": f, "value": list()})
            lines_new = []
            lines_origin = []
            if os.path.exists(os.path.join(path_new, f)):
                with open(os.path.join(path_new, f), "r", encoding=ENCONING) as file1:
                    lines_new = file1.readlines()
                    lines_new = [line.rstrip("\n") for line in lines_new]
            if os.path.exists(os.path.join(path_old, f)):
                with open(os.path.join(path_old, f), "r", encoding=ENCONING) as file2:
                    lines_origin = file2.readlines()
                    lines_origin = [line.rstrip("\n") for line in lines_origin]
            if len(lines_new) > len(lines_origin):
                for line in lines_new:
                    if not line.strip() in lines_origin:
                        miss_lines[-1]["value"].append(line)
                        l = [
                            i
                            for i, x in enumerate(lines_origin)
                            if line.split(";")[1] in x
                        ]
                        if l:
                            miss_lines[-1]["value"].append(f"({lines_origin[l[0]]})")
                        else:
                            miss_lines[-1]["value"].append(
                                ";".join(["" for x in line.split(";")])
                            )
            else:
                for row, line in enumerate(lines_origin, 1):
                    if not line.strip() in lines_new:
                        l = [
                            i
                            for i, x in enumerate(lines_new)
                            if line.split(";")[1] in x
                        ]
                        if l:
                            miss_lines[-1]["value"].append(
                                f"Т({l[0]}) = {lines_new[l[0]]}"
                            )
                        else:
                            miss_lines[-1]["value"].append(
                                "Т(0)  = " + ";".join(["" for x in line.split(";")])
                            )
                        miss_lines[-1]["value"].append(f"О({row}) = {line}")
        path_log = os.path.join(os.path.join(os.path.dirname(__file__), "log"))
        for item in miss_lines:
            if item["value"]:
                files_new.append(item["name"])
                with open(
                    os.path.join(
                        path_log,
                        f"{os.path.basename(path_old).split('_')[0]}_{item['name']}",
                    ),
                    "a",
                    encoding=ENCONING,
                ) as f:
                    f.writelines(map(lambda x: x + "\n", item["value"]))
        return files_new

    def __remove_download(self):
        if os.path.isdir(os.path.join(BASE_DIR, "test", "download", "old")):
            shutil.rmtree(os.path.join(BASE_DIR, "test", "download", "old"))
        if os.path.isdir(os.path.join(BASE_DIR, "test", "download", "new")):
            shutil.rmtree(os.path.join(BASE_DIR, "test", "download", "new"))
        if os.path.isdir(os.path.join(BASE_DIR, "test", "download", "test")):
            shutil.rmtree(os.path.join(BASE_DIR, "test", "download", "test"))
        if os.path.exists(
            os.path.join(BASE_DIR, "test", "download", self.parser.download_file)
        ):
            os.remove(
                os.path.join(BASE_DIR, "test", "download", self.parser.download_file)
            )

    def __check(self) -> tuple:
        path_download = os.path.join(BASE_DIR, "test", "download", "new")
        path_origin = os.path.join(BASE_DIR, "test", "download", "old")
        a = get_extract_files(
            archive_file={
                "file": os.path.join(
                    BASE_DIR, "test", "download", self.parser.download_file
                )
            },
            extract_dir=path_download,
            ext=r".csv",
        )
        b = get_extract_files(
            archive_file={
                "file": os.path.join(
                    BASE_DIR, "test", "origin", self.parser.download_file
                )
            },
            extract_dir=path_origin,
            ext=r".csv",
        )
        if a:
            path_download = os.path.dirname(a[0]["name"])
        if b:
            path_origin = os.path.dirname(b[0]["name"])
        if a == [] or b == []:
            return True, False

        os.makedirs(path_download, exist_ok=True)
        os.makedirs(path_origin, exist_ok=True)

        files_download = set(os.listdir(path_download))
        files_origin = set(os.listdir(path_origin))
        if len(files_download) == 0:
            return True, False

        # получаем все имена
        common = list(files_download | files_origin)

        # Теперь проверяем список common
        # на файлы, чтобы не попался каталог
        common_files = [
            file_name for file_name in common if re.search("csv", file_name)
        ]

        # Сравниваем общие файлы каталогов
        mismatch = self.__diff(path_download, path_origin, common_files)
        if os.path.isdir(path_download):
            rmtree(path_download)
        if os.path.isdir(path_origin):
            rmtree(path_origin)

        return mismatch, []

    def setUp(self):
        self.parser = Parser(
            file_name=os.path.join(BASE_DIR, "test", "input", "common.zip"),
            file_down=os.path.join(BASE_DIR, "test", "download", "test.zip"),
            union="output",
            path_down=os.path.join(BASE_DIR, "test", "download"),
        )

    # --------------------------------------------------------------------------------------
    def test_01_comfort(self):
        self.parser.name = os.path.join(BASE_DIR, "test", "input", "comfort.zip")
        self.parser.is_hash = IS_HASH
        self.parser.inn = "7801394857"
        self.parser.download_file = (
            f"comfort_{self.parser.inn}{'_no_hash' if self.parser.is_hash is False else ''}.zip"
        )
        self.__remove_download()
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_02_druzhba(self):
        self.parser.name = os.path.join(BASE_DIR, "test", "input", "druzhba.zip")
        self.parser.is_hash = IS_HASH
        self.parser.inn = "7802348243"
        self.parser.download_file = (
            f"druzhba_{self.parser.inn}{'_no_hash' if self.parser.is_hash is False else ''}.zip"
        )
        self.__remove_download()
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_03_molod(self):
        self.parser.name = os.path.join(BASE_DIR, "test", "input", "molod.zip")
        self.parser.is_hash = IS_HASH
        self.parser.inn = "4727000113"
        self.parser.download_file = (
            f"molod_{self.parser.inn}{'_no_hash' if self.parser.is_hash is False else ''}.zip"
        )
        self.__remove_download()
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_04_t414(self):
        self.parser.name = os.path.join(BASE_DIR, "test", "input", "414.zip")
        self.parser.is_hash = IS_HASH
        self.parser.inn = "7825455026"
        self.parser.download_file = (
            f"414_{self.parser.inn}{'_no_hash' if self.parser.is_hash is False else ''}.zip"
        )
        self.parser.is_hash = IS_HASH
        self.__remove_download()
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_05_t93(self):
        self.parser.is_hash = IS_HASH
        self.parser.name = os.path.join(BASE_DIR, "test", "input", "93.zip")
        self.parser.inn = "7806034914"
        self.parser.download_file = (
            f"93_{self.parser.inn}{'_no_hash' if self.parser.is_hash is False else ''}.zip"
        )
        self.__remove_download()
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_10_gefest(self):
        self.parser.is_hash = IS_HASH
        self.parser.name = os.path.join(BASE_DIR, "test", "input", "gefest.zip")
        self.parser.inn = "7801636143"
        self.parser.download_file = (
            f"gefest_{self.parser.inn}{'_no_hash' if self.parser.is_hash is False else ''}.zip"
        )
        self.__remove_download()
        if os.path.exists(
            os.path.join(BASE_DIR, "test", "download", self.parser.download_file)
        ):
            os.remove(
                os.path.join(BASE_DIR, "test", "download", self.parser.download_file)
            )
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_11_semiluki(self):
        self.parser.is_hash = IS_HASH
        self.parser.name = os.path.join(BASE_DIR, "test", "input", "semiluki.zip")
        self.parser.inn = "3628019094"
        self.parser.download_file = (
            f"semiluki_{self.parser.inn}{'_no_hash' if self.parser.is_hash is False else ''}.zip"
        )
        self.__remove_download()
        if os.path.exists(
            os.path.join(BASE_DIR, "test", "download", self.parser.download_file)
        ):
            os.remove(
                os.path.join(BASE_DIR, "test", "download", self.parser.download_file)
            )
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_12_7802064509(self):
        self.parser.is_hash = IS_HASH
        self.parser.name = os.path.join(BASE_DIR, "test", "input", "7802064509.zip")
        # self.parser.inn = "7802064509"
        self.parser.download_file = (
            f"7802064509{'_no_hash' if self.parser.is_hash is False else ''}.zip"
        )
        self.__remove_download()
        if os.path.exists(
            os.path.join(BASE_DIR, "test", "download", self.parser.download_file)
        ):
            os.remove(
                os.path.join(BASE_DIR, "test", "download", self.parser.download_file)
            )
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_99_shustoff(self):
        self.parser.name = os.path.join(BASE_DIR, "test", "input", "shustoff.zip")
        self.parser.is_hash = IS_HASH
        self.parser.inn = "5044110874"
        self.parser.download_file = (
            f"shustoff_{self.parser.inn}{'_no_hash' if self.parser.is_hash is False else ''}.zip"
        )
        self.__remove_download()
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)


@timing(
    start_message="Начало теста",
    end_message="окончание теста",
)
def main():
    try:
        unittest.main()
    except:
        pass


if __name__ == "__main__":
    path_log = os.path.join(os.path.join(os.path.dirname(__file__), "log"))
    os.makedirs(path_log, exist_ok=True)
    for f in os.listdir(path_log):
        os.remove(os.path.join(path_log, f))
    main()
