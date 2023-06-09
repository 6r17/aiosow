"""
await function(*args, **memory) -> this doesn't work because :
    - it is not generic and will break whenever a function doesn't take **kwargs
    - kwargs itself is a copy and will break reference
"""
from typing import Any, Callable, List

import inspect, logging, asyncio

ALIASES = {}


def get_aliases():  # pragma: no cover
    global ALIASES
    return ALIASES


def reset_aliases():  # pragma: no cover
    global ALIASES
    ALIASES = {}


def alias(name: str):
    """
    The alias function is a decorator that can be used to inject a value for a
    function argument that will be passed to the autofill function.

    When a function is decorated with alias, the arguments with the given name
    is aliased and its value will be replaced with the value returned by the
    aliased function when calling the autofill function. The original function
    can still be called normally, but when calling the autofill function,
    the arguments value will be determined by the registered alias.
    The registered alias function will be called and its result will be used as
    the argument value.

    **Args**:
    - name (str): The name of the argument to inject a value for.

    **Returns**:
    - Callable: A decorator that takes a function as input, registers it to have
      an injected argument with the given name, and returns the function unchanged.
    """

    def decorator(function: Callable):
        ALIASES[name] = function
        return function

    return decorator


async def fill_prototype(function: Callable, args: Any = [], **kwargs) -> Any:
    """
    The autofill function takes a callable function, args, and memory as input
    arguments, and returns the result of calling the function with autofilled
    arguments.

    **Args**:
    - function (Callable): The function to be called with autofilled arguments.
    - args (Any): A list of positional arguments to pass to the function.
    - memory (Any): A dictionary of keyword arguments to pass to the function.

    **Returns**:
    - Any: The result of calling the input function with autofilled arguments.

    **Notes**:
    - If the input function has default arguments, the corresponding values will
        be used if the input args and memory do not provide values for them.

    - If the input function has been decorated, this function will unwrap the
        original function and use its signature to determine the arguments.
    """
    memory = kwargs.get("memory", {})

    def prototype(function: Callable) -> List:
        return [
            (
                param_name,
                None
                if param.default is inspect.Parameter.empty
                else param.default,
            )
            for param_name, param in inspect.signature(
                function
            ).parameters.items()
            if param.kind != inspect.Parameter.VAR_KEYWORD
            and param.kind != inspect.Parameter.VAR_POSITIONAL
        ]

    class Sentinel:
        """Used to represent element to be deleted"""

    def none_to_empty(el):  # pragma: no cover
        if el == None:
            return []
        else:
            return el

    argscopy = list(args)
    if hasattr(function, "__wrapped__"):
        given_args = args
        kws = kwargs
        name = function.__wrapped__.__name__
    else:
        name = getattr(function, "__name__", None) or str(function)
        kws = kwargs if inspect.getfullargspec(function).varkw else {}
        prot = prototype(function)
        given_args = [
            memory
            if name == "memory"
            else await autofill(ALIASES[name], args=[], memory=memory)
            if name in ALIASES
            else argscopy.pop(0)
            if len(argscopy) > 0
            else (
                memory.get(name, value)
                if not name
                in none_to_empty(inspect.getfullargspec(function).varkw)
                else Sentinel
            )
            for (name, value) in prot
        ]
        given_args = [arg for arg in given_args if arg != Sentinel]
        has_varargs = any(
            param.kind == inspect.Parameter.VAR_POSITIONAL
            for param in inspect.signature(function).parameters.values()
        )
        given_args = (
            given_args if not has_varargs else given_args + list(argscopy)
        )
    return (name, given_args, kws)


def get_function_representation(function):
    name = function.__name__
    if name == "<lambda>":
        name = (
            inspect.getsource(function)
            .replace("\n", "")
            .replace("\t", "")
            .replace("    ", "")
        )
    return name


async def autofill(function: Callable, args: Any = [], **kwargs) -> Any:
    name, given_args, kws = await fill_prototype(function, args=args, **kwargs)
    try:
        if kwargs.get("memory", {}).get(
            "log_autofill", False
        ):  # pragma: no cover
            function_representation = get_function_representation(function)
            logging.info(f" -> {function_representation}")
        result = function(*given_args, **kws)
        return await result if inspect.iscoroutine(result) else result
    except Exception as err:  # pragma: no cover
        logging.error(f"{name} : {err}")
        logging.debug(f" > error generated by calling {name}({given_args})")
        raise (err)  # `debug` needs `autofill` to raise


def make_async(function: Callable) -> Callable:
    """
    Make a synchronous function run in it's own thread
    using `run_in_executor`.

    **args**:
    - function: Callable

    **returns**:
    - Async Callable
    """

    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        __name__, given_args, kws = await fill_prototype(
            function, args=args, **kwargs
        )
        return await loop.run_in_executor(None, function, *given_args, **kws)

    return wrapper


__all__ = ["alias", "autofill", "make_async", "fill_prototype"]
