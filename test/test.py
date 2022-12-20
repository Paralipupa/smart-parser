import unittest
import os
from shutil import rmtree
from module.utils import get_extract_files, get_hash_file
from module.parser import Parser
from module.settings import BASE_DIR


class TestGisConfig(unittest.TestCase):
    def __check(self) -> tuple:
        path_download = os.path.join(
            BASE_DIR, 'test', 'download', 'new')
        path_origin = os.path.join(
            BASE_DIR, 'test', 'download', 'old')
        a = get_extract_files(archive_file={'file': os.path.join(
            BASE_DIR, 'test', 'download', self.parser.download_file)}, extract_dir=path_download, ext=r'.csv')
        b = get_extract_files(archive_file={'file': os.path.join(
            BASE_DIR, 'test', 'origin', self.parser.download_file)}, extract_dir=path_origin, ext=r'.csv')
        hash_origin = set()
        hash_download = set()
        for item in a:
            hash_download.add(get_hash_file(item['name']))
        for item in b:
            hash_origin.add(get_hash_file(item['name']))
        if os.path.isdir(path_download):
            rmtree(path_download)
        if os.path.isdir(path_origin):
            rmtree(path_origin)

        return hash_origin, hash_download

    def setUp(self):
        self.parser = Parser(file_name=os.path.join(BASE_DIR, 'test', 'input', 'common.zip'),
                             file_down=os.path.join(
                                 BASE_DIR, 'test', 'download', 'test.zip'),
                             union='output',
                             path_down=os.path.join(BASE_DIR, 'test', 'download'))

    def test_druzhba(self):
        self.parser.name = os.path.join(
            BASE_DIR, 'test', 'input', 'druzhba.zip')
        self.parser.download_file = 'druzhba.zip'
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_gefest(self):
        self.parser.name = os.path.join(
            BASE_DIR, 'test', 'input', 'gefest.zip')
        self.parser.download_file = 'gefest.zip'
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_molod(self):
        self.parser.name = os.path.join(BASE_DIR, 'test', 'input', 'molod.zip')
        self.parser.download_file = 'molod.zip'
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)

    def test_shustoff(self):
        self.parser.name = os.path.join(
            BASE_DIR, 'test', 'input', 'shustoff.zip')
        self.parser.download_file = 'shustoff.zip'
        self.parser.start()
        hash_origin, hash_download = self.__check()
        self.assertEqual(hash_origin, hash_download)


if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as ex:
        print(f'{ex}')
