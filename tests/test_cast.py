from typing import Any, Callable, Dict
from functools import reduce
import inspect

def get_value_from_path(data: Dict, path: str, sep: str = ".") -> str:
    keys = path.split(sep)
    return reduce(lambda d, key: d.get(key) if d else None, keys, data)

def cast(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    argspec = inspect.getfullargspec(func)
    argnames = argspec.args
    defaults = argspec.defaults or []
    required_args = argnames[:-len(defaults)] if defaults else argnames
    positional_args = args[:len(required_args)]
    keyword_args = {arg: get_value_from_path(kwargs, arg) for arg in required_args[len(positional_args):]}
    all_args = positional_args + tuple(keyword_args[arg] for arg in argnames[len(positional_args):] if arg in keyword_args)
    return func(*all_args)

