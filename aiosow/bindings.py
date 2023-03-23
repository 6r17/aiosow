
from typing import Tuple, Callable, Any

import pdb as _pdb
import asyncio
import time
import inspect

from functools import wraps

from aiosow.autofill import autofill, alias
from aiosow.options import option
from aiosow.perpetuate import on, perpetuate
from aiosow.setup import setup

def wire() -> Tuple[Callable, Callable]:
    """
    Returns a tuple of two decorators: `trigger_decorator` and `listen_decorator`.

    The `trigger_decorator` decorator wraps an async function and triggers it,
    calling any functions registered  with the `listen_decorator` decorator. The
    `listen_decorator` decorator registers a function to be called whenever a
    function decorated with `trigger_decorator` is called.

    **Example**:
    ```
    wire_trigger, wire_listen = wire()

    @wire_listen
    def my_function():
        print("my_function called")

    @wire_trigger
    async def my_async_function():
        print("my_async_function called")

    await my_async_function()

    # will result with

    > my_async_function_called
    > my_function_called
    ```

    If the trigger function is a [`generator`](https://docs.python.org/3/glossary.html#term-generator), `wire` wil iterate over it
    and generate a singularized task for every element. [`generator`](https://docs.python.org/3/glossary.html#term-generator)
    are function which returns a generator iterator. It looks like a normal function except that it contains yield expressions for producing a series of values usable in a for-loop or that can be retrieved one at a time with the next() function.

    **Example**:
    ```
    wire_trigger, wire_listen = wire()

    @wire_listen
    def my_function(i):
        print(f"my_function called with {i}")

    @wire_trigger
    async def my_async_function(size):
        for i in range(size):
            yield i


    await my_async_function(2)

    # will result with

    > my_function_called with 0
    > my_function_called with 1
    ```


    **Returns**:
    - A tuple of two decorators: `trigger_decorator` and `listen_decorator`.
    """
    listeners = []
    def trigger_decorator(triggerer):
        @wraps(triggerer)
        async def call(*args, **kwargs):
            result = await autofill(triggerer, args=args, memory=kwargs['memory'])
            # if triggerer is a generator we need to iterate over it
            if result:
                if inspect.isgenerator(result):
                    tasks = []
                    for val in result:
                        tasks += [
                            asyncio.create_task(
                                autofill(func, args=[val], memory=kwargs['memory'])
                            ) for func in listeners if func
                        ]
                else:
                    tasks = [
                        asyncio.create_task(
                            autofill(func, args=[result], memory=kwargs['memory'])
                        ) for func in listeners if func
                    ]
                await asyncio.gather(*tasks)
            return result
        return call

    def listen_decorator(listener):
        listeners.append(listener)
        return listener

    return (trigger_decorator, listen_decorator)

def accumulator(size: int|Callable) -> Callable:
    """
    Batch the calls to a function. Triggers it when the bucket size is reached.
    If the size passed is a `Callable`, accumulator will call it with `memory`
    to get the size.
    """
    def decorator(function: Callable) -> Callable:
        bucket = []
        async def execute(*args, **kwargs) -> Any:
            nonlocal bucket
            if isinstance(size, Callable):
                _size = size(kwargs)
            else:
                _size = size
            bucket += args
            if len(bucket) >= _size:
                argument = bucket
                bucket = []
                return await autofill(function, args=[argument], memory=kwargs['memory'])
        return execute
    return decorator

def delay(seconds: float) -> Callable:
    """
    Makes sure the function takes at least `seconds` to run.
    It delays the execution of an asynchronous function by 
    `seconds - exec_time(function)` where `seconds` is a fixed delay time in 
    seconds and `exec_time(function)` is the time taken by the wrapped function
    to execute.

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
        @wraps(function)
        async def wrapper(*args, **kwargs):
            start_time = time.monotonic()
            result = await autofill(function, args=args, memory=kwargs['memory'])
            end_time = time.monotonic()
            exec_time = end_time - start_time
            delay = max(seconds - exec_time, 0)
            await asyncio.sleep(delay)
            return result
        return wrapper
    return decorator

def wrap(wrapper_function: Callable):
    """
    Wraps the result of a function with a given `wrapper_function`.

    **Args**:
    - wrapper_function: The function to use for wrapping the result of the
        decorated function.

    **Returns**:
    - A decorator that wraps the result of a function with the given
        `wrapper_function`.
    """
    def decorator(function: Callable):
        @wraps(function)
        async def execute(*args, **kwargs):
            result = await autofill(function, args=args, memory=kwargs['memory'])
            return wrapper_function(result)
        return execute
    return decorator

def each(iter:Callable|None=None):
    """
    Applies a function to each item in :
        - result of iter
        or
        - first argument passed to the resulting function

    **Args**:
    - iter: The async generator to iterate over.

    **Returns**:
    - A decorator that applies a function to each item returned by the given
        `iter`.
    """
    def decorator(function: Callable):
        @wraps(function)
        async def execute(*args, **kwargs):
            tasks = []
            if iter:
                subjects = await autofill(
                    iter, args=args, memory=kwargs['memory']
                )
                async for value in subjects:
                    tasks.append(
                        autofill(
                            function, args=(value,), memory=kwargs['memory']
                        )
                    )
            else:
                args = list(args)
                iterated = args.pop()
                for value in iterated:
                    tasks.append(autofill(
                        function, args=(value, args), memory=kwargs['memory'])
                    )
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
        @wraps(function)
        async def execute(*args, **kwargs):
            try:
                return await autofill(function, args=args, memory=kwargs['memory'])
            except Exception as e:
                trigger(e, function, args)
        return execute
    return decorator

def pdb(*__args__, **__kwargs__):
    """
    Launches pdb.set_trace(), utility function for `aiosow.bindings.debug`

    **Example**:
    ```
    function_to_debug = debug(pdb)(function_to_debug)
    ```
    """
    _pdb.set_trace()

def make_async(function: Callable) -> Callable:
    '''
    Make a synchronous function run in it's own thread
    using `run_in_executor`.

    **args**:
    - function: Callable

    **returns**:
    - Async Callable
    '''
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, function, (args, kwargs)
        )
    return wrapper

__all__ = [
    'alias', 'accumulator', 'autofill', 'delay', 'debug', 'each', 'make_async',
    'on', 'option', 'pdb', 'perpetuate', 'read_only', 'setup', 'wrap', 'wire' 
]
