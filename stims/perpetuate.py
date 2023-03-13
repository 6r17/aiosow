
from typing import Callable, Any

from stims.autofill import autofill

ONS = {}

def on(variable_name: str, condition: Callable|None=None):
    def decorator(function: Callable):
        if variable_name not in ONS:
            ONS[variable_name] = []
        ONS[variable_name].append((condition, function))
        return function
    return decorator

async def perpetuate(function: Callable, args: Any=[], kwargs: Any={}) -> Any:
    update = await autofill(function, args=args, kwargs=kwargs)
    if isinstance(update, dict):
        kwargs.update(update)
        for key, value in update.items():
            if key in ONS:
                for condition, func in ONS[key]:
                    if (condition and await autofill(condition, args=[value], kwargs=kwargs)) or not condition:
                        await autofill(func, args=args, kwargs=kwargs)
    return update
