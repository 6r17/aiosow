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
import logging

OPTIONS = {}


def option(name: str, **kwargs):  # pragma: no cover
    """
    Register an argparse option to be available using the command-line.

    **args**:
    - name: str -> the name of the option (will be used as f'--{name}')
    - kwargs: dict -> the options used by [argparse](https://docs.python.org/3/library/argparse.html)
    """
    global OPTIONS
    logging.debug("added new option %s", name)
    OPTIONS[name] = kwargs


def options():  # pragma: no cover
    global OPTIONS
    return OPTIONS


__all__ = ["option"]
