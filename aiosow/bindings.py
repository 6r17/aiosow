
from typing import Tuple, Callable, Any

import pdb as _pdb
import asyncio
import time
import functools

from functools import wraps

from aiosow.autofill import autofill, alias
from aiosow.options import option
from aiosow.perpetuate import on, perpetuate
from aiosow.setup import setup


def wire() -> Tuple[Callable, Callable]:
    """
    Returns a tuple of two decorators: `trigger_decorator` and `listen_decorator`.

    The `trigger_decorator` decorator wraps an async function and triggers it, calling any functions registered 
    with the `listen_decorator` decorator. The `listen_decorator` decorator registers a function to be called 
    whenever a function decorated with `trigger_decorator` is called.

    **Example**:
    ```
    wire_trigger, wire_listen = wire()

    @wire_listen
    def my_function():
        print("my_function called")

    @wire_trigger
    async def my_async_function():
        print("my_async_function called")
    ```

    In the above example, calling `my_async_function()` will print "my_async_function called", and 
    then call `my_function()` to print "my_function called".

    **Returns**:
    - A tuple containing two decorators: `trigger_decorator` and `listen_decorator`.
    """
    listeners = []
    def trigger_decorator(triggerer):
        @wraps(triggerer)
        async def call(*args, **kwargs):
            result = await autofill(triggerer, args=args, kwargs=kwargs)
            tasks = [
                asyncio.create_task(
                    autofill(func, args=args, kwargs=kwargs)
                ) for func in listeners if func
            ]
            await asyncio.gather(*tasks)
            return result
        return call

    def listen_decorator(listener):
        listeners.append(listener)
        return listener

    return (trigger_decorator, listen_decorator)

def delay(seconds: float):
    """
    Decorator that makes sure the function takes at least `seconds` to run.
    It delays the execution of an asynchronous function by 
    ```
    seconds - exec_time(function)
    ```
    where `seconds` is a fixed delay time in seconds and `exec_time(function)` 
    is the time taken by the wrapped function to execute.

    **Args**:
    - seconds: The fixed delay time in seconds.

    **Returns**:
    - A decorator that can be used to wrap an asynchronous function.

    **Example**:
    ```
        @delay(2.5)
        async def my_function():
            # code here
    ```
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
    """
    Returns a decorator that wraps the result of a function with a given `wrapper_function`.

    The returned decorator can be used to decorate an async function. When the decorated function is called,
    it first calls `autofill` to fill in any missing arguments, then passes the result of the function to 
    `wrapper_function`, and finally returns the wrapped result.

    **Args**:
    - wrapper_function: The function to use for wrapping the result of the decorated function.

    **Returns**:
    - A decorator that wraps the result of a function with the given `wrapper_function`.
    """
    def decorator(function: Callable):
        @functools.wraps(function)
        async def execute(*args, **kwargs):
            result = await autofill(function, args=args, kwargs=kwargs)
            return wrapper_function(result)
        return execute
    return decorator

def each(iterated_generator: Callable):
    """
    Returns a decorator that applies a function to each item returned by an async generator.

    The returned decorator can be used to decorate an async function. When the decorated function is called,
    it first calls `autofill` to fill in any missing arguments, then calls the `iterated_generator` to get an
    async generator, and finally applies the decorated function to each item returned by the generator.

    **Args**:
    - iterated_generator: The async generator to iterate over.

    **Returns**:
    - A decorator that applies a function to each item returned by the given `iterated_generator`.
    """
    def decorator(function: Callable):
        @functools.wraps(function)
        async def execute(*args, **kwargs):
            iterated = await autofill(iterated_generator, args=args, kwargs=kwargs)
            tasks = []
            async for value in iterated:
                tasks.append(autofill(function, args=(value,), kwargs=kwargs))
            return await asyncio.gather(*tasks)
        return execute
    return decorator

def read_only(something: Any) -> Callable:
    """
    Wraps a value in a function.

    **Example**:
    ```
    getter = read_only(2)
    getter() -> 2 
    ```


    **Args**:
    - something: Any

    **Returns**:
    - getter: Callable
    """
    def getter():
        nonlocal something
        return something
    return getter

def debug(trigger: Callable[[Exception, Callable, Tuple], Any]) -> Callable:
    """
    Return a decorator that calls `trigger` when the decorated entity raises
    an error.

    **Example**:
    ```
    function_to_debug = debug(pdb)(function_to_debug)
    ```

    **`trigger` is called with**:
    - error: Exception
    - function: Callable
    - args: tuple

    **Args**:
    - triggered: Callable

    **Returns**:
    - decorator: Callable
    """
    def decorator(function: Callable) -> Callable:
        @functools.wraps(function)
        async def execute(*args, **kwargs):
            try:
                return await autofill(function, args=args, kwargs=kwargs)
            except Exception as e:
                trigger(e, function, args)
        return execute
    return decorator

def pdb(*__args__, **__kwargs__):
    """
    Launches pdb.set_trace(), incorporated as a utility function for `aiosow.bindings.debug`

    **Example**:
    ```
    function_to_debug = debug(pdb)(function_to_debug)
    ```
    """
    _pdb.set_trace()

__all__ = ['alias', 'delay', 'wrap', 'each', 'option', 'on', 'setup', 'perpetuate', 'autofill', 'read_only', 'debug', 'pdb']
