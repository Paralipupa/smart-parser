import unittest
import os, sys
from shutil import rmtree
import filecmp
import difflib as df
from module.utils import get_extract_files, get_hash_file
from module.parser import Parser
from module.settings import BASE_DIR
from module.settings import ENCONING


class TestGisConfig(unittest.TestCase):

    def __diff(self, path1: str, path2: str, files: list):
        miss_lines = list()
        for file in files:
            miss_lines.append({'name':file,'value':list()})
            file1 = open(os.path.join(path1,file), "r", encoding=ENCONING)
            file2 = open(os.path.join(path2,file), "r", encoding=ENCONING)
            lines1 = file1.readlines()
            lines1 = [line.rstrip('\n') for line in lines1]
            lines2 = file2.readlines()
            lines2 = [line.rstrip('\n') for line in lines2]

            if len(lines1) == len(lines2):
                for line in lines1:
                    if not line.strip() in lines2:
                        miss_lines[-1]['value'].append(line)
                        l = [i for i,x in enumerate(lines2) if line.split(';')[1] in x]
                        if l:
                            miss_lines[-1]['value'].append(lines2[l[0]])
                        else:
                            miss_lines[-1]['value'].append('не найден')
        for item in miss_lines:
            with open(os.path.join(os.path.dirname(path2),f"{item['name']}.log"), 'w' ) as file:
                file.writelines( map (lambda x: x + '\n', item['value']) );
        return miss_lines

    def __check(self) -> tuple:
        path_download = os.path.join(
            BASE_DIR, 'test', 'download', 'new')
        path_origin = os.path.join(
            BASE_DIR, 'test', 'download', 'old')
        a = get_extract_files(archive_file={'file': os.path.join(
            BASE_DIR, 'test', 'download', self.parser.download_file)}, extract_dir=path_download, ext=r'.csv')
        b = get_extract_files(archive_file={'file': os.path.join(
            BASE_DIR, 'test', 'origin', self.parser.download_file)}, extract_dir=path_origin, ext=r'.csv')

        path_download = os.path.dirname(a[0]['name'])
        path_origin = os.path.dirname(b[0]['name'])

        files_download = set(os.listdir(path_download))
        files_origin = set(os.listdir(path_origin))

        # получаем общие имена
        common = list(files_download & files_origin)

        # Теперь проверяем список common
        # на файлы, чтобы не попался каталог
        common_files = [file_name for file_name in common]

        # Сравниваем общие файлы каталогов
        match, mismatch, errors = filecmp.cmpfiles(
            path_download,
            path_origin,
            common_files,
        )
        if mismatch:
            self.__diff(path_download, path_origin, mismatch)
        if os.path.isdir(path_download):
            rmtree(path_download)
        if os.path.isdir(path_origin):
            rmtree(path_origin)

        return mismatch, errors

    def setUp(self):
        self.parser = Parser(file_name=os.path.join(BASE_DIR, 'test', 'input', 'common.zip'),
                             file_down=os.path.join(
                                 BASE_DIR, 'test', 'download', 'test.zip'),
                             union='output',
                             path_down=os.path.join(BASE_DIR, 'test', 'download'))

    # def test_druzhba(self):
    #     self.parser.name = os.path.join(
    #         BASE_DIR, 'test', 'input', 'druzhba.zip')
    #     self.parser.download_file = 'druzhba.zip'
    #     self.parser.start()
    #     hash_origin, hash_download = self.__check()
    #     self.assertEqual(hash_origin, hash_download)

    # def test_gefest(self):
    #     self.parser.name = os.path.join(
    #         BASE_DIR, 'test', 'input', 'gefest.zip')
    #     self.parser.download_file = 'gefest.zip'
    #     self.parser.start()
    #     hash_origin, hash_download = self.__check()
    #     self.assertEqual(hash_origin, hash_download)

    # def test_molod(self):
    #     self.parser.name = os.path.join(BASE_DIR, 'test', 'input', 'molod.zip')
    #     self.parser.download_file = 'molod.zip'
    #     self.parser.start()
    #     hash_origin, hash_download = self.__check()
    #     self.assertEqual(hash_origin, hash_download)

    def test_shustoff(self):
        self.parser.name = os.path.join(
            BASE_DIR, 'test', 'input', 'shustoff.zip')
        self.parser.download_file = 'shustoff.zip'
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)


if __name__ == "__main__":
    unittest.main()
