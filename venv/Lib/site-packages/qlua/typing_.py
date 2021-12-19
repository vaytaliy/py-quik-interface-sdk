"""
Описание типов данных.
"""
# pylint: disable=pointless-statement,multiple-statements,unused-argument
# pylint: disable=too-few-public-methods,super-init-not-called

import sys
import argparse
from typing import (
    Optional,
    Union,
)
if sys.version_info < (3, 8, 0):
    try:
        from typing_extensions import (  # pylint: disable=no-name-in-module,unused-import
            Protocol, runtime_checkable,
        )
    except ImportError:
        raise ImportError('Для Python<3.8 необходимо установить MyPy: '
                          "'pip install mypy'")
else:
    from typing import (  # type: ignore # pylint: disable=no-name-in-module,unused-import
        Protocol, runtime_checkable,
    )


TExitCode = Optional[Union[bool, int]]


@runtime_checkable
class PArgparseSubmodule(Protocol):
    """Протокол подмодуля, инициирующего argparse submodule."""
    def __init__(self, parser: argparse.ArgumentParser) -> None:
        """Настройка parser"""
    def __call__(self, args: argparse.Namespace) -> TExitCode:
        """Действие при активации подмодуля."""
