
import logging
from typing import Callable
from stims.autofill import autofill

RUN_FUNCTION: Callable|None = None

def run(function: Callable):
    global RUN_FUNCTION
    RUN_FUNCTION = function
    return function

async def do_run(kwargs):
    global RUN_FUNCTION
    if RUN_FUNCTION:
        logging.info(f'Running {RUN_FUNCTION.__module__}.{RUN_FUNCTION.__name__}')
        await autofill(RUN_FUNCTION, kwargs=kwargs)
    else:
        logging.info('There is no function bound as main')
