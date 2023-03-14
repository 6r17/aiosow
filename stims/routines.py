
import logging
from typing import Callable

import aiojobs, asyncio

from stims.run import run
from stims.setup import setup
from stims.perpetuate import perpetuate, autofill
from stims.bindings import delay

ROUTINES = []

def clear_routines():
    global ROUTINES
    ROUTINES = []

def get_routines():
    global ROUTINES
    return ROUTINES

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

@delay(1)
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

async def consume_routines_forever(kwargs): # pragma: no cover
    '''Loop forever and calls consume_routine on every call'''
    while True:
        logging.debug('Scheduler heart-beat')
        await consume_routines(kwargs)

@setup
async def scheduler(kwargs): # pragma: no cover
    '''Uses aiojobs scheduler to spawn a 2nd execution queue'''
    scheduler = aiojobs.Scheduler()
    job = await scheduler.spawn(consume_routines_forever(kwargs))
    return { 'routine_job': job, 'scheduler': scheduler }

@run
async def wait_for_scheduler(routine_job):
    await routine_job.wait()
