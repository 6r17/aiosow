from typing import Tuple,Callable

import asyncio
from functools import wraps

from stims.autofill import autofill


def wire() -> Tuple[Callable, Callable]:
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
