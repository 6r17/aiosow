from typing import Callable

import asyncio

from aiosow.setup import setup
from aiosow.perpetuate import perpetuate, autofill
from aiosow.bindings import delay

ROUTINES = []


def clear_routines():
    global ROUTINES
    ROUTINES = []


def get_routines():
    global ROUTINES
    return ROUTINES


def routine(
    interval: int,
    life=0,
    repeat=True,
    condition: Callable | None = None,
    perpetuate=True,
) -> Callable:
    """
    Specifies a function to be executed as a routine.

    **args**:
    - interval : the interval at which the routine should run
    - function : the function to run
    - repeat : wether it should repeat
    - life : the initial amount of time before next trigger
    - condition : to prevent the triggering
    - perpetuate : wether the result should be saved in memory
    """

    def decorator(fn: Callable) -> Callable:
        ROUTINES.append(
            {
                "interval": interval,
                "function": fn,
                "repeat": repeat,
                "life": life,
                "condition": condition,
                "perpetuate": perpetuate,
            }
        )
        return fn

    return decorator


@delay(1)
async def consume_routines(memory):
    for routine in ROUTINES:
        routine["life"] = routine["life"] - 1
        if routine["life"] <= 0:
            if routine["perpetuate"]:
                await perpetuate(routine["function"], memory=memory)
            else:
                await autofill(routine["function"], memory=memory)
            if routine["repeat"]:
                routine["life"] = routine["interval"]
            else:
                ROUTINES.remove(routine)


async def consumer(memory):  # pragma: no cover
    while True:
        await autofill(consume_routines, memory=memory)


@setup
async def spawn_consumer(memory):  # pragma: no cover
    return asyncio.create_task(consumer(memory))


__all__ = ["routine"]
