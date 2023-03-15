import logging

errors = []

class InfoFilter(logging.Filter):
    def __init__(self, *args, **kwargs):
        super(InfoFilter, self).__init__()

    def filter(self, record):
        return record.levelname == 'INFO'

class DebugFilter(logging.Filter):
    def __init__(self, *args, **kwargs):
        super(DebugFilter, self).__init__()

    def filter(self, record):
        return record.levelname == 'DEBUG'

class WarningFilter(logging.Filter):
    def __init__(self, *args, **kwargs):
        super(WarningFilter, self).__init__()

    def filter(self, record):
        return record.levelname == 'WARNING'

class ErrorFilter(logging.Filter):
    def __init__(self, *args, **kwargs):
        super(ErrorFilter, self).__init__()

    def filter(self, record):
        if (record.levelname == 'ERROR' or record.levelname == 'CRITICAL'):
            text = ''
            if record.exc_text != None:
                text = record.exc_text
            elif record.exc_info != None:
                text = f"{record.name}:{record.lineno}"
            if text and len(errors) > 0 and (text in errors):
                return False
            errors.append(text)
            return record.levelname == 'ERROR' or record.levelname == 'CRITICAL'
        else:
            return False

class CustomFormatter(logging.Formatter):
    
    def __init__(self, *args, **kwargs):
        super().__init__()
        grey = f"{chr(27)}[38m"
        green = f"{chr(27)}[32m"
        yellow = f"{chr(27)}[33m"
        red = f"{chr(27)}[31m"
        bold_red = f"{chr(27)}[31;1m"
        reset = f"{chr(27)}[0m"
        format = kwargs.get('format', "[%(levelname)s %(asctime)s] - {0}%(message)s{1}")
        self.datefmt = kwargs.get('datefmt', "%d-%m-%Y %H:%M:%S")
        self.FORMATS = {
            logging.DEBUG: format.format(green,reset),
            logging.INFO: format.format(grey,reset),
            logging.WARNING: format.format(yellow,reset),
            logging.ERROR: format.format(red,reset),
            logging.CRITICAL: format.format(bold_red,reset) 
        }

    def format(self, record,  *args, **kwargs):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)

