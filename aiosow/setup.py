import logging, asyncio
from typing import Dict, List, Callable
from aiosow.perpetuate import perpetuate

SETUP_FUNCTIONS: List = []

def clear_setups(): # pragma: no cover
    global SETUP_FUNCTIONS
    SETUP_FUNCTIONS = []

def setup(func: Callable) -> Callable:
    """
    Decorator to add a function to the list of initialization functions.

    **Args**:
    - func (Callable): Function to add to the list of initialization functions.

    **Returns**:
    - func (Callable): The same function, unchanged.
    """
    SETUP_FUNCTIONS.append(func)
    return func

async def initialize(kwargs: Dict) -> List[asyncio.Task]:
    """
    Function that runs all initialization functions added to the list.

    Args:
        - app (web.Application): The aiohttp application.
        - mem (Dict): The mem dictionary.
    """
    logging.debug(
        'initialize with %s',
        [f'{fn.__name__}' for fn in SETUP_FUNCTIONS]
    )
    tasks = []
    for setup_func in SETUP_FUNCTIONS:
        result = await perpetuate(setup_func, kwargs=kwargs)
        if asyncio.iscoroutine(result):
            tasks.append(result)
        logging.debug(f'{setup_func.__module__}.{setup_func.__name__} : ok')
    return tasks

__all__ = ['setup']
