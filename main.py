import sys
from module.utils import getArgs
from module.parser import Parser
from datetime import datetime
from module.settings import *
import shutil

if __name__ == "__main__":

    if False and IS_DELETE_TMP:
        if os.path.isdir(PATH_LOG):
            shutil.rmtree(PATH_LOG)
        if os.path.isdir(PATH_OUTPUT):
            shutil.rmtree(PATH_OUTPUT)
        if os.path.isdir(PATH_TMP):
            shutil.rmtree(PATH_TMP)

    args = getArgs()
    namespace = args.parse_args(sys.argv[1:])
    parser = Parser(file_name=namespace.name, inn=namespace.inn, file_config=namespace.config,
                    union=namespace.union, path_down=PATH_DOWNLOAD, hash=namespace.hash,
                    file_down=f'{namespace.inn if namespace.inn else "output"}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.zip')
    parser.start()
