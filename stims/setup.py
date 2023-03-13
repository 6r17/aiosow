import logging
from typing import Dict, List, Callable
from aiohttp import web


SETUP_FUNCTIONS: List = []
logger = logging.getLogger(__name__)


def setup(func: Callable) -> Callable:
    """
    Decorator to add a function to the list of initialization functions.

    Args:
        func (Callable): Function to add to the list of initialization functions.

    Returns:
        func (Callable): The same function, unchanged.
    """
    SETUP_FUNCTIONS.append(func)
    return func


async def initialize(kwargs: Dict) -> None:
    """
    Function that runs all initialization functions added to the list.

    Args:
        app (web.Application): The aiohttp application.
        mem (Dict): The mem dictionary.
    """
    for setup_func in SETUP_FUNCTIONS:
        try:
            await setup_func(kwargs)
        except Exception as e:
            logger.error(f"An error occurred while running {setup_func.__name__}: {e}")

