from typing import Callable
from functools import wraps

import asyncio, logging

from aiosow.perpetuate import perpetuate, autofill
from aiosow.bindings import return_true


def infinite_generator(condition: Callable):
    def _generator_consumer(function: Callable):
        """Re-autofill a generator function at end of it's loop"""

        iterated = None

        @wraps(function)
        async def __generator_consumer(*args, **kwargs):
            nonlocal iterated
            while await autofill(condition, args=args, **kwargs):
                if not iterated:
                    iterated = await autofill(function, args=args, **kwargs)
                try:
                    return await iterated.__anext__()
                except StopAsyncIteration:
                    iterated = await autofill(function, args=args, **kwargs)
                    return await iterated.__anext__()

        return __generator_consumer

    return _generator_consumer


ROUTINES = []


def clear_routines():
    global ROUTINES
    ROUTINES = []


def get_routines():
    global ROUTINES
    return ROUTINES


def routine(
    frequency: int | float,
    condition: Callable = return_true,
    timeout: int = -1,
    perpetuate=True,
) -> Callable:
    """
    Specifies a function to be executed as a routine.
    **args**:
    - frequency : the frequency at which the routine should run
    - condition : to prevent the triggering
    - perpetuate : wether the result should be saved in memory
    """

    def decorator(fn: Callable) -> Callable:
        logging.info("+ routine %s", fn.__name__)
        ROUTINES.append(
            {
                "frequency": frequency,
                "timeout": timeout if timeout >= 0 else abs(frequency),
                "function": fn,
                "condition": condition,
                "perpetuate": perpetuate,
            }
        )
        return fn

    return decorator


async def consume_routines(memory):
    routines = get_routines()
    # Find the routine with the smallest remaining timeout or a timeout <= 0
    smallest_timeout_routine = min(routines, key=lambda x: x["timeout"])
    smallest_timeout = smallest_timeout_routine["timeout"]

    # Wait until the smallest timeout has elapsed
    await asyncio.sleep(smallest_timeout)

    # Execute any routines that have timed out
    for routine in routines:
        routine["timeout"] -= smallest_timeout
        routine["timeout"] = 0 if routine["timeout"] < 0 else routine["timeout"]
        if routine["timeout"] <= 0:
            condition = routine["condition"]
            function = routine["function"]
            # Check the condition before running the routine
            try:
                if await autofill(condition, args=[], memory=memory):
                    if routine["perpetuate"]:
                        await perpetuate(function, args=[], memory=memory)
                    else:
                        await autofill(function, args=[], memory=memory)
            except Exception as err:
                logging.error(err)
                if memory.get("raise", False):
                    raise (err)
            # Update the timeout value based on the frequency
            if routine["frequency"] > 0:
                routine["timeout"] = routine["frequency"]
            else:
                routines.remove(routine)


async def routine_consumer(memory):  # pragma: no cover
    while True:
        await autofill(consume_routines, memory=memory)


async def spawn_routine_consumer(memory):  # pragma: no cover
    return asyncio.create_task(routine_consumer(memory))


__all__ = ["routine", "infinite_generator"]
