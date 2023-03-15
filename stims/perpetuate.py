
import logging
import asyncio
from typing import Callable, Any
from collections.abc import Iterable

from stims.autofill import autofill

ONS = {}

def on(variable_name: str, condition: Callable|None=None, singularize=False):
    def decorator(function: Callable):
        if variable_name not in ONS:
            ONS[variable_name] = []
        ONS[variable_name].append((condition, function, singularize))
        return function
    return decorator

async def perpetuate(function: Callable, args: Any=[], kwargs: Any={}) -> Any:
    update = await autofill(function, args=args, kwargs=kwargs)
    if isinstance(update, dict):
        kwargs.update(update)
        logging.debug('Update of memory : %s', update)
        for key, value in update.items():
            if key in ONS:
                for (condition, func, singularize) in ONS[key]:
                    if singularize:
                        if not isinstance(value, Iterable):
                            raise ValueError('Singularize received a non iterable value')
                        await asyncio.gather(*[autofill(func, args=[iterated], kwargs=kwargs) for iterated in value])
                    else:
                        if (condition and await autofill(condition, args=[value], kwargs=kwargs)) or not condition:
                            await autofill(func, args=[value], kwargs=kwargs)
    return update
