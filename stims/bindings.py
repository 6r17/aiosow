
from typing import Callable, Union

import asyncio
import time
import functools

from stims.autofill import autofill

# this is used to gather decorators for test and documentation
DECORATORS = []
def decorator(function: Callable):
    DECORATORS.append(function)
    return function

@decorator
def delay(seconds: float):
    """
    Decorator that delays the execution of an asynchronous function by 
    `seconds - exec_time(function)`, where `seconds` is a fixed delay time in 
    seconds and `exec_time(function)` is the time taken by the wrapped function
    to execute.

    Args:
        seconds: The fixed delay time in seconds.

    Returns:
        A decorator that can be used to wrap an asynchronous function.

    Example usage:
        @delay(seconds=2.5)
        async def my_function():
            # code here
    """
    def decorator(function: Callable):
        @functools.wraps(function)
        async def wrapper(*args, **kwargs):
            start_time = time.monotonic()
            result = await autofill(function, args=args, kwargs=kwargs)
            end_time = time.monotonic()
            exec_time = end_time - start_time
            delay = max(seconds - exec_time, 0)
            await asyncio.sleep(delay)
            return result
        return wrapper
    return decorator

def wrap(wrapper_function: Callable):
    def decorator(function: Callable):
        @functools.wraps(function)
        async def execute(*args, **kwargs):
            result = await autofill(function, args=args, kwargs=kwargs)
            return wrapper_function(result)
        return execute
    return decorator

def each(iterated_generator: Callable):
    def decorator(function: Callable):
        async def execute(*args, **kwargs):
            iterated = await autofill(iterated_generator, args=args, kwargs=kwargs)
            tasks = []
            async for value in iterated:
                tasks.append(autofill(function, args=(value,), kwargs=kwargs))
            return await asyncio.gather(*tasks)
        return execute
    return decorator
