class InnMismatchException(Exception):
    def __init__(self):
        self._message = "ИНН не соответствует конфигурации"
        super(InnMismatchException, self).__init__(self._message)

class FatalException(Exception):
    def __init__(self, msg : str):
        self._message = msg
        super(FatalException, self).__init__(self._message)

class ConfigNotFoundException(Exception):
    def __init__(self):
        self._message = "Не найдены параметры конфигурации"
        super(InnMismatchException, self).__init__(self._message)

