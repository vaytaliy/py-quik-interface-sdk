"""
Примеры использования API.

Поддержка исполнения через CLI.
"""

import argparse
from typing import Generator, Tuple, Dict
import logging
from ..typing_ import (
    runtime_checkable,
    Protocol,
    TExitCode,
    PArgparseSubmodule,
)

# WRNING: Не забудь отредактировать EXAMPLES!
from . import (
    rpc,
    # api,
)


log = logging.getLogger(__name__)


@runtime_checkable  # pylint: disable=too-few-public-methods
class PExample(Protocol):
    """Протокол примеров использования."""
    @staticmethod
    def main(url: str, user: str, passwd: str) -> TExitCode:
        """Запуск примера."""


TExamples = Dict[str, PExample]


# Объекты, используемые в качестве примеров, доступных через CLI.
EXAMPLES: TExamples = {
    i.__name__.split('.')[-1]: i
    for i in (
        rpc,
        # api,
        # << Добавь новый модуль сюда.
    )
    if isinstance(i, PExample)
}


class Argparser(PArgparseSubmodule):
    """Добавляет аргуметны командной строки к argparser."""
    # pylint: disable=super-init-not-called,too-few-public-methods
    examples: TExamples = EXAMPLES

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('example_name', type=str, help='Название примера',
                            choices=EXAMPLES.keys())
        parser.add_argument('url', type=str, help=('Адрес Quik RPC в формате: '
                                                   '"tcp://127.0.0.1:5560"'))
        parser.add_argument('user', type=str, help='Имя пользователя Quik RPC')
        parser.add_argument('passwd', type=str, help='Пароль Quik RPC')

    def __call__(self, args: argparse.Namespace) -> TExitCode:
        """Выполняет действия при вызове из командной строки."""
        log.debug('Выполняю пример: %s', args.example_name)
        example_module: PExample = self.examples[args.example_name]
        exit_code: TExitCode = example_module.main(
            url=args.url,
            user=args.user,
            passwd=args.passwd,
        )
        return exit_code
