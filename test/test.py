import os
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


class TestGisConfig(unittest.TestCase):
    def __diff(self, path_new: str, path_old: str, files: list) -> list:
        miss_lines = list()
        files_new = []
        for f in files:
            miss_lines.append({"name": f, "value": list()})
            with open(os.path.join(path_new, f), "r", encoding=ENCONING) as file1:
                lines1 = file1.readlines()
                lines1 = [line.rstrip("\n") for line in lines1]
            with open(os.path.join(path_old, f), "r", encoding=ENCONING) as file2:
                lines2 = file2.readlines()
                lines2 = [line.rstrip("\n") for line in lines2]
            if len(lines1) > len(lines2):
                for line in lines1:
                    if not line.strip() in lines2:
                        miss_lines[-1]["value"].append(line)
                        l = [i for i, x in enumerate(lines2) if line.split(";")[1] in x]
                        if l:
                            miss_lines[-1]["value"].append(lines2[l[0]])
                        else:
                            miss_lines[-1]["value"].append(
                                ";".join(["" for x in line.split(";")])
                            )
            else:
                for row, line in enumerate(lines2,1):
                    if not line.strip() in lines1:
                        l = [i for i, x in enumerate(lines1) if line.split(";")[1] in x]
                        if l:
                            miss_lines[-1]["value"].append(f'{l[0]} = {lines1[l[0]]}')
                        else:
                            miss_lines[-1]["value"].append("  = " +
                                ";".join(["" for x in line.split(";")])
                            )
                        miss_lines[-1]["value"].append(f'{row} = {line}')
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

        os.makedirs(path_download, exist_ok=True)
        os.makedirs(path_origin, exist_ok=True)

        files_download = set(os.listdir(path_download))
        files_origin = set(os.listdir(path_origin))
        if len(files_download) == 0:
            return True, False

        # получаем общие имена
        common = list(files_download & files_origin)

        # Теперь проверяем список common
        # на файлы, чтобы не попался каталог
        common_files = [file_name for file_name in common]

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

    def test_shustoff(self):
        self.parser.name = os.path.join(
            BASE_DIR, 'test', 'input', 'shustoff.zip')
        self.parser.download_file = 'shustoff.zip'
        self.__remove_download()
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)


    def test_druzhba(self):
        self.parser.name = os.path.join(BASE_DIR, "test", "input", "druzhba.zip")
        self.parser.download_file = "druzhba.zip"
        self.__remove_download()
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_gefest(self):
        self.parser.name = os.path.join(
            BASE_DIR, 'test', 'input', 'gefest.zip')
        self.parser.download_file = 'gefest.zip'
        self.__remove_download()
        if os.path.exists(os.path.join(
                BASE_DIR, 'test', 'download', self.parser.download_file)):
            os.remove(os.path.join(
                BASE_DIR, 'test', 'download', self.parser.download_file))
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_molod(self):
        self.parser.name = os.path.join(BASE_DIR, 'test', 'input', 'molod.zip')
        self.parser.download_file = 'molod.zip'
        self.__remove_download()
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_t414(self):
        self.parser.name = os.path.join(BASE_DIR, 'test', 'input', '414.zip')
        self.parser.download_file = '414.zip'
        self.parser.inn = '7825455026'
        self.__remove_download()
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

@timing(
    start_message="Начало теста",
    end_message="окончание теста",
)
def main():
    unittest.main()

if __name__ == "__main__":
    path_log = os.path.join(os.path.join(os.path.dirname(__file__), "log"))
    os.makedirs(path_log, exist_ok=True)
    for f in os.listdir(path_log):
        os.remove(os.path.join(path_log, f))
    main()
