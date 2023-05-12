from typing import Tuple, Callable, Any, Union

import pdb as _pdb
import asyncio
import time
import inspect
from functools import wraps

from aiosow.autofill import autofill, alias, make_async
from aiosow.options import option
from aiosow.perpetuate import on, perpetuate
from aiosow.setup import setup


# def adapter(resolve: Callable) -> Callable:
#    def wrapper(function: Callable) -> Callable:
#        async def caller(item, **kwargs):
#            value = await autofill(resolve, args=[item], **kwargs)
#            result = await autofill(function, args=[value], **kwargs)
#            return result
#
#        return caller
#
#    return wrapper


def chain(*functions):
    """Applies functions iteratively and pass each result to next function"""

    async def _chain(*args, **kwargs):
        result = None
        has_result = False
        for function in functions:
            sig = inspect.getfullargspec(function)
            result = await perpetuate(
                function, args=[result] if has_result else list(args), **kwargs
            )
            if sig.annotations.get("return") is not inspect._empty:
                has_result = True
        return result

    return _chain


def until_success():
    delay = 1

    def retry_until_success(function: Callable):
        async def call(*args, **kwargs):
            nonlocal delay
            while True:
                try:
                    result = await autofill(function, args=args, **kwargs)
                    delay = 1
                    return result
                except:
                    if delay < 1200:
                        delay = delay * 2
                    await asyncio.sleep(delay)

        return call

    return retry_until_success


def wire(condition=None, perpetual=False, pass_args=True) -> Tuple[Callable, Callable]:
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
    caster = autofill if not perpetual else perpetuate

    def trigger_decorator(triggerer):
        @wraps(triggerer)
        async def call(*args, **kwargs):
            result = await autofill(triggerer, args=args, **kwargs)
            # if triggerer is a generator we need to iterate over it
            if result and (
                await autofill(condition, args=[], **kwargs) if condition else True
            ):
                if inspect.isgenerator(result):
                    tasks = []
                    for val in result:
                        tasks += [
                            asyncio.create_task(
                                caster(func, args=[val] if pass_args else [], **kwargs)
                            )
                            for func in listeners
                            if func
                        ]
                else:
                    tasks = [
                        asyncio.create_task(
                            caster(func, args=[result] if pass_args else [], **kwargs)
                        )
                        for func in listeners
                        if func
                    ]
                await asyncio.gather(*tasks)
            return result

        return call

    def listen_decorator(listener):
        listeners.append(listener)
        return listener

    return (trigger_decorator, listen_decorator)


def accumulator(size: Union[int, Callable]) -> Callable:
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
                _size = size(kwargs.get("memory", {}))
            else:
                _size = size
            bucket += args
            if len(bucket) >= _size:
                argument = bucket
                bucket = []
                return await autofill(function, args=[argument], **kwargs)

        return execute

    return decorator


def call_limit(seconds):
    """
    A decorator that limits the frequency of function calls based on the number
    of seconds specified in the decorator parameter.

    **Args**:
        - seconds (int): The minimum number of seconds that must elapse between
            function calls.

    **Returns**:
        - function: A decorated function that can only be called once every
            `seconds` seconds.
    """

    def decorator(func):
        last_called = 0

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_called
            if time.monotonic() - last_called >= seconds:
                try:
                    result = await autofill(func, args=args, **kwargs)
                    last_called = time.monotonic()
                    return result
                except Exception as e:
                    last_called = time.monotonic()
                    raise e
            else:
                await asyncio.sleep(seconds - (time.monotonic() - last_called))
                result = await autofill(func, args=args, **kwargs)
                last_called = time.monotonic()
                return result

        return wrapper

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
            result = await autofill(function, args=args, **kwargs)
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
            result = await autofill(function, args=args, **kwargs)
            return wrapper_function(result)

        return execute

    return decorator


def each(iter: Union[Callable, None] = None):
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
                subjects = await autofill(iter, args=args, **kwargs)
                async for value in subjects:
                    tasks.append(autofill(function, args=(value,), **kwargs))
            else:
                args = list(args)
                iterated = args.pop()
                for value in iterated:
                    tasks.append(autofill(function, args=(value, args), **kwargs))
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
                return await autofill(function, args=args, **kwargs)
            except Exception as e:
                trigger(e, function, args)

        return execute

    return decorator


def return_true(*__args__):
    """
    Python doesn't allow lambda definition inside prototype
    This function is used as a default value for conditional parameters that
    take a function to filter behavior.
    """
    return True


def return_false(*__args__):
    """
    Python doesn't allow lambda definition inside prototype
    This function is used as a default value for conditional parameters that
    take a function to filter behavior.
    """
    return False


def do_raise(exception):
    """
    Python doesn't allow lambda definition inside prototype
    This function is used as a default value for conditional parameters that
    allow custom definition of behavior on exception.
    """

    raise exception


def dont_raise(__exception__):
    """
    Python doesn't allow lambda definition inside prototype
    This function is used as a default value for conditional parameters that
    allow custom definition of behavior on exception.
    """


def expect(
    trigger: Callable,
    condition: Callable = return_true,
    retries=float("inf"),
    on_raise=do_raise,
) -> Callable:
    """
    Decorated function is retried after perpetuation of trigger function on
    Exception.
    """

    def decorator(function: Callable) -> Callable:
        counter = 0
        delay = 1

        @wraps(function)
        async def _expect(*args, **kwargs):
            nonlocal counter, delay
            try:
                result = await autofill(function, args=args, **kwargs)
                counter = 0
                return result
            except Exception as raised_error:
                if counter >= retries:
                    on_raise(raised_error)
                elif condition(args, raised_error):
                    counter += 1
                    await asyncio.sleep(delay)
                    delay = delay * 2
                    await perpetuate(trigger, args=[], **kwargs)
                    return await _expect(*args, **kwargs)
                else:
                    on_raise(raised_error)

        return _expect

    return decorator


def pdb(*__args__, **__kwargs__):  # pragma: no cover
    """
    Launches pdb.set_trace(), utility function for `aiosow.bindings.debug`

    **Example**:
    ```
    function_to_debug = debug(pdb)(function_to_debug)
    ```
    """
    _pdb.set_trace()


__all__ = [
    "alias",
    "accumulator",
    "autofill",
    "delay",
    "debug",
    "each",
    "make_async",
    "on",
    "option",
    "pdb",
    "perpetuate",
    "read_only",
    "setup",
    "wrap",
    "wire",
]
