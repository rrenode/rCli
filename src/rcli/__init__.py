import sys
import logging
import sys

#from rcli import __version__

__author__ = "rrenode"
__copyright__ = "rrenode"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "rCli"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

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