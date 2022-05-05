import configparser
import os

class GisConfig:

    def __init__(self, filename : str):
        self._is_init = False
        if self.is_exist(filename):
            self._config = configparser.ConfigParser()
            self._config.read(filename)
            self._init_configuration()

    def is_exist(self, filename : str) -> bool:
        return os.path.exists(filename)
    
    def _init_configuration(self):

        self._condition_range = ""
        self._condition_column = ""
        self._condition_range = "(.)+"
        self._columns_heading = ""
        self._row_start = int(self._config["main"]["row_start"])
        self._page_name = self._config["main"]["page_name"]
        self._page_index = int(self._config["main"]["page_index"])
        self._max_cols = int(self._config["main"]["max_columns"])
        self._max_rows_heading = int(self._config["main"]["max_rows_heading"])

        num_cols = int(self._config["main"]["columns_count"])
        self._columns_heading = [self._config[f"col_{i}"]["pattern"] for i in range(num_cols)]
        for i in range(num_cols):
            try:
                self._condition_range = self._config[f"col_{i}"]["condition_range"]
                self._condition_column = self._config[f"col_{i}"]["pattern"]
                break
            except:
                pass
        self._is_init = True

        

