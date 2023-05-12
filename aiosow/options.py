"""
When writing your own compositions you may want to add additionnal options to the
command-line.

You do it using the option function.

**Example:**
```
option('keyword', default='foo', help='Keyword to use')
```

Any option defined is propagated into the memory, in fact the initial memory is
a copy of the parsed arguments.
"""

OPTIONS = []
COMMANDS = []


def option(*args, **kwargs):  # pragma: no cover
    """
    Register an argparse option to be available using the command-line.

    **args**:
    - name: str -> the name of the option (will be used as f'--{name}')
    - kwargs: dict -> the options used by [argparse](https://docs.python.org/3/library/argparse.html)
    """
    global OPTIONS
    OPTIONS.append((args, kwargs))


def command(name):  # pragma: no cover
    """
    Register an argparse command to be available using the command-line.

    **args**:
    - name: str -> the name of the option (will be used as f'--{name}')
    - kwargs: dict -> the options used by [argparse](https://docs.python.org/3/library/argparse.html)
    """
    global COMMANDS

    def register(function):
        COMMANDS.append((name, function))
        return function

    return register


def options():  # pragma: no cover
    global OPTIONS
    return OPTIONS


def commands():  # pragma: no cover
    global COMMANDS
    return COMMANDS


__all__ = ["option", "command"]
