from typing import Dict, Type

class SingletonMeta(type):
    _instances: Dict[Type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class CommandRegistry(metaclass=SingletonMeta):
    """A singleton registry for CLI subcommands."""
    def __init__(self):
        self._commands: Dict[str, object] = {}

    def register(self, handler: object, name: str = None):
        if name == None:
            name = handler.__name__
        self._commands[name] = handler

    def get(self, name: str):
        return self._commands.get(name)

    def all_commands(self):
        return dict(self._commands)
