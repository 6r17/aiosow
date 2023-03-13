
from typing import Callable, Any

from stims.autofill import autofill


async def perpetuate(function: Callable, args: Any=[], kwargs: Any={}) -> Any:
    # update = await function(*args, **kwargs)
    update = await autofill(function, args=args, kwargs=kwargs)
    if isinstance(update, dict):
        kwargs.update(update)
    # kwargs.update(update)
    return update
