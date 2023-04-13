import abc
import csv
import os

from openpyxl import load_workbook
import xlrd


def rchop(s, sub):
    return s[: -len(sub)] if s.endswith(sub) else s


class DataFile(abc.ABC):
    def __init__(self, fname, sheet_name, first_line, columns, page_index: int = 0):
        self._fname = fname
        self._first_line = first_line
        self._sheet_name = sheet_name
        self._columns = columns
        self._page_index = page_index
        self._sheet = None

    def __iter__(self):
        return self

    def __next__(self):
        return ""


class CsvFile(DataFile):
    def __init__(self, fname, first_line, address_columns, page_index=None):
        super(CsvFile, self).__init__(fname, "", first_line, address_columns)
        self._freader = open(fname, "r", encoding="cp1251")
        self._first_line = first_line
        self._reader = csv.reader(self._freader, delimiter=";", quotechar="|")
        self._line_num = 0

    def get_row(self, row):
        index = 0
        for cell in row:
            if index in self._columns:
                yield XlsFile.get_cell_text(cell)
            index = index + 1

    def __next__(self):
        for row in self._reader:
            self._line_num += 1
            if self._line_num < self._first_line:
                continue
            return row
        raise StopIteration

    def __del__(self):
        self._freader.close()


class XlsFile(DataFile):
    def __init__(self, fname, sheet_name, first_line, address_columns, page_index=0):
        super(XlsFile, self).__init__(fname, sheet_name, first_line, address_columns)
        # with xlrd.open_workbook(fname, logfile=open(os.devnull, 'w')) as wb:
        with xlrd.open_workbook(fname) as wb:
            if self._sheet_name:
                self._sheet = wb.sheet_by_name(self._sheet_name)
            else:
                self._sheet = wb.sheets()[page_index]
            self._rows = (
                self._sheet.row(index) for index in range(first_line, self._sheet.nrows)
            )

    @staticmethod
    def get_cell_text(cell):
        if cell.ctype == 2:
            return rchop(str(cell.value), ".0")
        return str(cell.value)

    def get_row(self, row):
        index = 0
        for cell in row:
            if index in self._columns:
                yield XlsFile.get_cell_text(cell)
            index = index + 1

    def __next__(self):
        for row in self._rows:
            return list(self.get_row(row))
        raise StopIteration

    def __del__(self):
        pass


class XlsxFile(DataFile):
    def __init__(self, fname, sheet_name, first_line, columns, page_index=-1):
        super(XlsxFile, self).__init__(
            fname, sheet_name, first_line, columns, page_index
        )
        try:
            self._wb = load_workbook(filename=fname)
        except:
            self._wb = load_workbook(filename=fname, read_only=True)

    def get_sheet(self) -> object:
        for sh in self._wb.worksheets:
            if (self._sheet_name or self._page_index != -1) and self._sheet is not None:
                raise StopIteration
            if self._sheet_name:
                self._sheet = self._wb.get_sheet_by_name(self._sheet_name)
            elif self._page_index != -1:
                self._sheet = self._wb.worksheets[self._page_index]
            else:
                self._sheet = sh
            self._cursor = self._sheet.iter_rows()
            yield self._sheet

    @staticmethod
    def get_cell_text(cell):
        return str(cell.value) if cell.value != None else ""

    def get_row(self, row):
        i = 0
        for cell in row:
            if i in self._columns:
                yield XlsxFile.get_cell_text(cell)
            i += 1

    def __next__(self):
        return list(self.get_row(next(self._cursor)))

    def __del__(self):
        self._wb.close()

    def get_index(self, cell):
        try:
            return cell.column
        except AttributeError:
            return -1


def get_file_reader(fname):
    """Get class for reading file as iterable"""
    _, file_extension = os.path.splitext(fname)
    # if file_extension == '.csv':
    #     return CsvFile
    if file_extension == ".xls":
        return XlsFile
    if file_extension == ".xlsx":
        # return XlsFile
        return XlsxFile
    if file_extension == ".csv":
        return CsvFile
    raise Exception("Unknown file type")
