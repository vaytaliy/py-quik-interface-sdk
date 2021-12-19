"""
Пакет для работы с Quik LUA RPC.
"""

import os
from configparser import ConfigParser
import logging
from pkg_resources import resource_filename


logging.getLogger(__name__).addHandler(logging.NullHandler())

META = ConfigParser()
META.read(resource_filename(__name__, os.path.join('conf', 'meta.ini')))

__author__ = META['default']['author']
__version__ = META['default']['version']
__email__ = META['default']['email']
__url__ = META['default']['url']
