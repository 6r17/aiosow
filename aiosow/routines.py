from typing import Callable

import asyncio, logging

from aiosow.setup import setup
from aiosow.perpetuate import perpetuate, autofill
from aiosow.bindings import return_true

ROUTINES = []


def clear_routines():
    global ROUTINES
    ROUTINES = []


def get_routines():
    global ROUTINES
    return ROUTINES


def routine(
    frequency: int, condition: Callable = return_true, timeout: int = -1
) -> Callable:
    """
    Specifies a function to be executed as a routine.

    **args**:
    - frequency : the frequency at which the routine should run
    - condition : to prevent the triggering
    - perpetuate : wether the result should be saved in memory
    """

    def decorator(fn: Callable) -> Callable:
        ROUTINES.append(
            {
                "frequency": frequency,
                "timeout": timeout if timeout >= 0 else abs(frequency),
                "function": fn,
                "condition": condition,
            }
        )
        return fn

    return decorator


async def consume_routines(memory):
    ROUTINES = get_routines()
    while ROUTINES:
        # Calculate the smallest timeout value among all routines
        smallest_timeout = min([routine["timeout"] for routine in ROUTINES])
        # Update the timeout value for each routine
        for routine in ROUTINES:
            routine["timeout"] -= smallest_timeout
        # Check if any routines have timed out
        for routine in ROUTINES:
            if routine["timeout"] == 0:
                condition = routine["condition"]
                function = routine["function"]
                # Check the condition before running the routine
                try:
                    if await autofill(condition, args=[], memory=memory):
                        await perpetuate(function, args=[], memory=memory)
                except:
                    pass
                # Update the timeout value based on the frequency
                if routine["frequency"] > 0:
                    routine["timeout"] = routine["frequency"]
                else:
                    ROUTINES.remove(routine)
        # Wait until the next routine is scheduled to run
        await asyncio.sleep(smallest_timeout)


async def consumer(memory):  # pragma: no cover
    while True:
        await autofill(consume_routines, memory=memory)


async def spawn_consumer(memory):  # pragma: no cover
    return asyncio.create_task(consumer(memory))


__all__ = ["routine"]
