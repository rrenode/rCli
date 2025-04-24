import os
import importlib.util
import sys
from pathlib import Path
from typing import List, Optional

from logging import getLogger

from .registry import CommandRegistry

logger = getLogger("rCli.commands")
registry = CommandRegistry()

class CommandHandler:
    # Class-level dictionary to store commands
    commands = {}
        
    """Abstract base for all subcommand handlers."""
    def run(self, args: List[str], ctx: Optional[str] = None):
        raise NotImplementedError("Subcommands must implement run()")
    
    @classmethod
    def command(cls, name):
        """Command decorator that registers methods as commands at the class level."""
        def decorator(func):
            if not hasattr(cls, 'commands'):
                cls.commands = {}
            cls.commands[name] = func
            return func
        return decorator

def auto_import_subcommands(commands_dir: str) -> None:
    """Automatically imports all Python files in the commands directory to register subcommands."""
    commands_path = Path(commands_dir)

    # Check if the provided directory exists
    if not commands_path.is_dir():
        return
    
    # Recursively import all Python files in the commands directory
    for file in commands_path.rglob("*.py"):  # This searches for all .py files recursively
        module_name = file.stem  # Get the module name (file name without .py)

        # If the module is already in sys.modules, reload it to ensure it's executed
        if module_name in sys.modules:
            module = sys.modules[module_name]
            importlib.reload(module)
        else:
            # Dynamically import the module using importlib
            spec = importlib.util.spec_from_file_location(module_name, str(file))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # Execute the module to apply decorators
            sys.modules[module_name] = module

def cog(name_or_cls=None):
    """Decorator to register a subcommand handler."""

    def decorator(command_cls):
        # If no name is provided, use the class's name (lowercased)
        if isinstance(name_or_cls, str):
            name = name_or_cls  # The name was passed directly as a string
        elif name_or_cls is None:
            name = command_cls.__name__.lower()  # Use the lowercase class name if no name is provided
        else:
            # In case name_or_cls is a class, we need to handle this case
            name = name_or_cls.__name__.lower()

        logger.debug(f"Registering subcommand '{name}' for class {command_cls.__name__}")  # Debugging print
        # Register the class handler for the subcommand name
        registry.register(command_cls, name)
        return command_cls

    return decorator

CmdHandler = CommandHandler