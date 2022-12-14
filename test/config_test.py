import unittest
import os
from module.parser import Parser
from module.settings import BASE_DIR


class TestGisConfig(unittest.TestCase):
    def setUp(self):
        self.parser = Parser(file_name=os.path.join(BASE_DIR, 'test', 'input', 'common.zip'),
                             file_down=os.path.join(BASE_DIR, 'test', 'download','test.zip'),
                             union='output',
                             path_down=os.path.join(BASE_DIR, 'test', 'download'))

    def test_druzhba(self):
        self.parser.name = os.path.join(BASE_DIR, 'test', 'input', 'druzhba.zip')
        self.parser.download_file = 'druzhba.zip'
        self.parser.start()
        self.assertEqual(10, 10)

    def test_gefest(self):
        self.parser.name = os.path.join(BASE_DIR, 'test', 'input', 'gefest.zip')
        self.parser.download_file = 'gefest.zip'
        self.parser.start()
        self.assertEqual(10, 10)

    def test_molod(self):
        self.parser.name = os.path.join(BASE_DIR, 'test', 'input', 'molod.zip')
        self.parser.download_file = 'molod.zip'
        self.parser.start()
        self.assertEqual(10, 10)

    def test_shustoff(self):
        self.parser.name = os.path.join(BASE_DIR, 'test', 'input', 'shustoff.zip')
        self.parser.download_file = 'shustoff.zip'
        self.parser.start()
        self.assertEqual(10, 10)


if __name__ == "__main__":
    unittest.main()
