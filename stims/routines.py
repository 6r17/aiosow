
from typing import Callable

import aiojobs, asyncio

from stims.setup import setup
from stims.perpetuate import perpetuate, autofill
from stims.bindings import delay, decorator

ROUTINES = []

def clear_routines():
    global ROUTINES
    ROUTINES = []

def get_routines():
    global ROUTINES
    return ROUTINES

@decorator
def routine(interval: int, life=0, repeat=True, condition: Callable|None=None, perpetuate=True) -> Callable:
    def decorator(fn: Callable) -> Callable:
        ROUTINES.append({
            "interval": interval,
            "function": fn,
            "repeat": repeat,
            "life": life,
            "condition": condition,
            "perpetuate": perpetuate
        })
        return fn
    return decorator

async def consume_routines(kwargs):
    for routine in ROUTINES:
        routine["life"] = routine["life"] - 1
        if routine["life"] <= 0:
            if routine['perpetuate']:
                await perpetuate(routine['function'], kwargs=kwargs)
            else:
                await autofill(routine['function'], kwargs=kwargs)
            if routine["repeat"]:
                routine["life"] = routine["interval"]
            else:
                ROUTINES.remove(routine)

async def run(kwargs): # pragma: no cover
    '''Loop forever and calls consume_routine on every call'''
    while True:
        await consume_routines(kwargs)

async def spawn_routine_manager(kwargs): # pragma: no cover
    '''Uses aiojobs scheduler to spawn a 2nd execution queue'''
    scheduler = aiojobs.Scheduler()
    await scheduler.spawn(run(kwargs))
