"""
Реализация основного интерфейса командной строки.
"""

import sys
assert sys.version_info > (3, 7, 0), "Для использования необходим Python>=3.7"
import argparse
from ast import literal_eval
from dataclasses import dataclass
import logging
import logging.config
from typing import Type, Any, Dict
from pkg_resources import resource_filename
from .typing_ import TExitCode, PArgparseSubmodule
from . import __version__, examples
if __debug__:
    try:
        import yaml  # pylint disable=import-error
    except ImportError:
        pass


log = logging.getLogger(__name__)

@dataclass
class ArgparseSubmodule:
    """Модель данных для настройки подмодуля argparse."""
    name: str
    action: Type[PArgparseSubmodule]
    params: Dict[str, Any]


# Кортеж подмодулей CLI.
ARGPARSE_SUBMODULES = (
    ArgparseSubmodule(
        'example',
        examples.Argparser,
        {'help': 'Примеры',
         'description': 'Примеры использования библиотеки'}
    ),
)


def logging_conf(filename_prod: str = 'conf/logging.conf',
                 filename_dev: str = 'conf/logging-dev.yaml') -> None:
    """Настройка логов."""
    def production() -> None:
        """Настройка логов для продакшана."""
        with open(resource_filename(__name__, filename_prod)) as file:
            content = literal_eval(file.read())
            logging.config.dictConfig(content)

    def development() -> bool:
        """Настройка логов для разработки."""
        try:
            with open(resource_filename(__name__, filename_dev)) as file:
                logging.config.dictConfig(yaml.safe_load(file))
        except OSError:
            return False
        except NameError:
            raise ImportError("Для logging-dev.yaml требуется пакет 'pyyaml'."
                              "Для установки выполните: 'pip install pyyaml'")
        except yaml.YAMLError as msg:
            raise SyntaxError(f'Ошибка настроки логов: {filename_dev}\n{msg}')
        return True

    if __debug__:
        if development():
            return
    production()


def argparse_conf() -> TExitCode:
    """Настройка парсера аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog='qlua',
        description='Python Quik LUA API'
    )
    parser.add_argument('-v', '--version', action='store_true',
                        help='Вывод версии программы')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Вывод сообщений отладки')
    subparsers = parser.add_subparsers(title='Действия')

    for i in ARGPARSE_SUBMODULES:
        subparser = subparsers.add_parser(i.name, **i.params)
        action = i.action(subparser)
        subparser.set_defaults(action=action)

    args = parser.parse_args()

    if args.version:
        print(__version__)
        return True
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        log.debug('Включен режим отладки.')
    if 'action' in args:
        assert isinstance(args.action, PArgparseSubmodule)
        return args.action(args)
    return False


def main() -> int:
    '''Стартовый скрипт'''
    logging_conf()
    exit_code: TExitCode = argparse_conf()
    if exit_code is None:
        return 0
    if exit_code is True:
        return 0
    if exit_code is False:
        return 1
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
