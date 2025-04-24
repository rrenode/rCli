"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = rcli.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import logging
import sys

from rcli import __version__

__author__ = "rrenode"
__copyright__ = "rrenode"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users

import sys

from .registry import CommandRegistry
from .commands import auto_import_subcommands
from .parser import parse_args

class rCli:
    def __init__(self):
        auto_import_subcommands("commands")
        self.registry = CommandRegistry()
        
        self.__parse__()
    
    @property
    def commands(self):
        return self.registry.all_commands()
    
    @commands.setter
    def commands(self, value):
        raise Exception("Do not set the commands for rCli. Instead use rCli().register_command(handler, name) or alternitively register with rCli.CommandRegistry().register(handler, name)")
    
    def register_command(self, handler, name):
        self.registry.register(handler, name)
    
    def __parse__(self):
        self.raw_args = sys.argv
        self.args = parse_args(self.raw_args)