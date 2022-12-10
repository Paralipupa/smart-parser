import sys
from module.utils import getArgs
from module.parser import Parser
from datetime import datetime
from module.settings import *

if __name__ == "__main__":
    args = getArgs()
    namespace = args.parse_args(sys.argv[1:])
    parser = Parser(file_name=namespace.name, inn=namespace.inn, file_config=namespace.config,
                    union=namespace.union, path_down=PATH_OUTPUT, hash=namespace.hash, 
                    file_down=f'output_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.zip')
    parser.start()
