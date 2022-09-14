import sys
from module.utils import getArgs
from module.parser import Parser

if __name__ == "__main__":
    args = getArgs()
    namespace = args.parse_args(sys.argv[1:])
    parser = Parser(namespace.name, namespace.inn, namespace.config,namespace.union)
    parser.start()
