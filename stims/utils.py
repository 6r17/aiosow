from functools import reduce
from typing import Any

def get_value_by_path(data, path, separator="__") -> Any:
    keys = path.split(separator)
    try:
        return reduce(lambda d, key: d[int(key)] if isinstance(d, list) else d[key], keys, data)
    except (KeyError, IndexError, TypeError):
        return None

