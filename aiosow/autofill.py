'''
await function(*args, **kwargs) -> this doesn't work if the function doesnt take **kwargs
'''
from typing import Any, Callable, List

import inspect, logging 

ALIASES = {}

def get_aliases(): # pragma: no cover
    global ALIASES
    return ALIASES

def reset_aliases(): # pragma: no cover
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

async def autofill(function: Callable, args: Any=[], kwargs: Any={}) -> Any:
    """
    The autofill function takes a callable function, args, and kwargs as input
    arguments, and returns the result of calling the function with autofilled
    arguments.

    **Args**:
    - function (Callable): The function to be called with autofilled arguments.
    - args (Any): A list of positional arguments to pass to the function.
    - kwargs (Any): A dictionary of keyword arguments to pass to the function.

    **Returns**:
    - Any: The result of calling the input function with autofilled arguments.

    **Notes**:
    - If the input function has default arguments, the corresponding values will
        be used if the input args and kwargs do not provide values for them.
   
    - If the input function has been decorated, this function will unwrap the 
        original function and use its signature to determine the arguments.
    """

    def prototype(function:Callable) -> List:
        return [
            (param_name, None if param.default is inspect.Parameter.empty else param.default)
            for param_name, param in inspect.signature(function).parameters.items()
            if param.kind != inspect.Parameter.VAR_KEYWORD
            and param.kind != inspect.Parameter.VAR_POSITIONAL
        ]
    
    class Sentinel:
        '''Used to represent element to be deleted'''
    
    argscopy = list(args)
    if hasattr(function, '__wrapped__'):
        given_args = args
        kws = kwargs
        name = function.__wrapped__.__name__
    else:
        name = getattr(function, '__name__', None) or str(function)
        kws = kwargs if inspect.getfullargspec(function).varkw else {}
        prot = prototype(function)
        given_args = [
            await autofill(ALIASES[name], args=args, kwargs=kwargs) if name in ALIASES else
            argscopy.pop(0) if len(argscopy) > 0 else
            (kwargs.get(name, value) if not inspect.getfullargspec(function).varkw else Sentinel)
            for (name, value) in prot 
        ]
        given_args = [arg for arg in given_args if arg != Sentinel]
        has_varargs = any(param.kind == inspect.Parameter.VAR_POSITIONAL for param in inspect.signature(function).parameters.values())
        given_args = given_args if not has_varargs else given_args + list(argscopy)
    if kwargs['log_autofill']:
        logging.debug('%s(%s, %s)', name, given_args, kwargs)
    result = function(*given_args, **kws )
    return await result if inspect.iscoroutine(result) else result

__all__ = ['alias', 'autofill']