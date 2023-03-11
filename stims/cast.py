from functools import reduce
from typing import Any

def get_value_by_path(dictionary: dict, path: str, separator:str="__") -> Any:
    return reduce(
        lambda d, key: d.get(key) if d else None,
        path.split(separator),
        dictionary
    )
