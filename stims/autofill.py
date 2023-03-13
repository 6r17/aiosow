'''
await function(*args, **kwargs) -> this doesn't work if the function doesnt take
**kwargs
'''
from typing import Any, Callable, List

import inspect

def prototype(function:Callable) -> List:
    return [
        (param_name, None if param.default is inspect.Parameter.empty else param.default)
        for param_name, param in inspect.signature(function).parameters.items()
    ]

async def autofill(function: Callable, args: Any=[], kwargs: Any={}) -> Any:
    argscopy = list(args)
    kws = kwargs if inspect.getfullargspec(function).varkw else {}
    result = function(*[
            argscopy.pop(0) if len(argscopy) > 0 else kwargs.get(name, value)
            for (name, value) in prototype(function)
        ], **kws 
    )
    return await result if inspect.iscoroutinefunction(function) else result
