from dataclasses import dataclass, field
from typing import List, Dict, Set, Any
import re

@dataclass
class CliArgs:
    program: str = ""
    global_options: Dict[str, str] = field(default_factory=dict)
    global_flags: Set[str] = field(default_factory=set)
    command: str = ""
    subcommands: List[str] = field(default_factory=list)
    local_options: Dict[str, str] = field(default_factory=dict)
    local_flags: Set[str] = field(default_factory=set)
    positionals: List[str] = field(default_factory=list)
    context_args: List[str] = field(default_factory=list) 
    
def parse_args(args: list[str]) -> CliArgs:
    parsed_args = pa = CliArgs()
    pa.program = args.pop(0)

    passed_global_scope = False

    def current_scope():
        return ("global_options", "global_flags") if not passed_global_scope else ("local_options", "local_flags")

    def set_option(name: str, value: str):
        opt_dict, _ = current_scope()
        target = getattr(pa, opt_dict)
        if name in target:
            # Append to existing list-style values
            target[name] += f",{value}"
        else:
            target[name] = value

    def set_flag(name: str):
        _, flag_set = current_scope()
        getattr(pa, flag_set).add(name)

    def parse():
        nonlocal passed_global_scope
        while args:
            arg = args.pop(0)
            
            # Handle context-symbol-prefixed args
            context_prefixes = ["/", "?#", "?@", "??"]
            if any(arg.startswith(prefix) for prefix in context_prefixes):
                pa.context_args.append(arg)
                passed_global_scope = True
            # --key=value
            elif re.match(r"^--[\w-]+=.+$", arg):
                name, val = arg[2:].split("=", 1)
                set_option(name, val)
            # --flag or --key (space-separated value)
            elif re.match(r"^--[\w-]+$", arg):
                name = arg[2:]
                if args and not args[0].startswith("-"):
                    val = args.pop(0)
                    set_option(name, val)
                else:
                    set_flag(name)
            # -abc (combined short flags)
            elif re.match(r"^-[a-zA-Z]{2,}$", arg):
                for ch in arg[1:]:
                    set_flag(ch)
            # -x value
            elif re.match(r"^-[a-zA-Z]$", arg):
                name = arg[1:]
                if args and not args[0].startswith("-"):
                    val = args.pop(0)
                    set_option(name, val)
                else:
                    set_flag(name)
            # "Search queries as command"
            elif re.match(r"^[@:#].+", arg):
                pa.command = arg  # e.g., @alias, :name, #id
            # Command
            elif not pa.command:
                pa.command = arg
                passed_global_scope = True
            # First subcommand
            elif not pa.subcommands:
                pa.subcommands.append(arg)
            # Positionals
            else:
                pa.positionals.append(arg)

    parse()
    return pa

def reconstruct_args(parsed: CliArgs, ignore_global=False, ignore_program=True) -> List[str]:
    args = []

    if not ignore_program:
        args.append(parsed.program)

    # Add context arguments first
    args.extend(parsed.context_args)

    if parsed.command:
        args.append(parsed.command)

    # Add global options
    if not ignore_global:
        for name, value in parsed.global_options.items():
            if ',' in value:
                for val in value.split(','):
                    args.append(f"--{name}={val}")
            else:
                args.append(f"--{name}={value}")

        for flag in parsed.global_flags:
            args.append(f"--{flag}")

    args.extend(parsed.subcommands)

    for name, value in parsed.local_options.items():
        if ',' in value:
            for val in value.split(','):
                args.append(f"--{name}={val}")
        else:
            args.append(f"--{name}={value}")

    for flag in parsed.local_flags:
        args.append(f"--{flag}")

    args.extend(parsed.positionals)

    return args
