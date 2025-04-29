import importlib
import pkgutil
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
    """Automatically imports all Python modules in the commands directory."""
    if getattr(sys, 'frozen', False):
        # PyInstaller EXE mode
        print("[rCli] Running in frozen mode. Importing submodules dynamically.")
        package_name = commands_dir.replace('/', '.').replace('\\', '.')
        import_frozen_submodules(package_name)
    else:
        # Normal filesystem mode
        commands_path = Path(commands_dir)

        if not commands_path.is_dir():
            return
        
        print("[rCli] Importing subcommands from filesystem.")
        
        # Import manually by scanning files
        for file in commands_path.rglob("*.py"):
            if file.name == "__init__.py":
                continue  # Skip __init__.py
            
            # Build full module path
            rel_path = file.relative_to(Path.cwd())
            module_name = ".".join(rel_path.with_suffix('').parts)
            print(f"[rCli] Importing {module_name}")

            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                importlib.import_module(module_name)

def import_frozen_submodules(package_name: str) -> None:
    """Import all submodules when running frozen."""
    for loader, module_name, is_pkg in pkgutil.walk_packages(None, prefix=package_name + "."):
        # Only import modules that are direct children of our package
        if not module_name.startswith(package_name + "."):
            continue
        if "._" in module_name:
            # Skip private/internal frozen modules
            continue

        print(f"[rCli] Importing frozen module {module_name}")
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)

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