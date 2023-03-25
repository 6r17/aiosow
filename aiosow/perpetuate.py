import logging, json
import asyncio
from typing import Callable, Any
from collections.abc import Iterable

from aiosow.autofill import autofill

ONS = {}


def on(variable_name: str, condition: Callable | None = None, singularize=False):
    """
    Decorator function that registers a function to be executed when a variable
    of specified name is perpetuated in memory.

    **Args**:
    - variable_name (str): Name of the event to listen to.
    - condition (Callable|None, optional): Callable object that takes the value
        of the event as input and returns a boolean indicating whether the
        registered function should be executed or not. Defaults to None.
    - singularize (bool, optional): Boolean indicating whether the value of the
        event should be singularized before being passed as an argument to the
        registered function. If True, the value must be iterable. Defaults to
        False.

    **Returns**:
    - The decorated function.

    **Example**:
    ```
    @on('pages')
    async def manage_pages(*args, memory):
        # code to send a welcome email to the user
    ```
    **note**: the decorated function is perpetuated and autofilled which means
    that it's result will be propegated to the memory and that it's arguments
    are autofilled based on it.
    """

    def decorator(function: Callable):
        if variable_name not in ONS:
            ONS[variable_name] = []
        ONS[variable_name].append((condition, function, singularize))
        return function

    return decorator


async def perpetuate(function: Callable, args: Any = [], memory: Any = {}) -> Any:
    """
    Asynchronously executes a function and perpetuates its effects in memory.

    **Args**:
    - function (Callable): The function to be executed.
    - args (Any, optional): Positional arguments to be passed to the function.
        Defaults to an empty list.
    - memory: The memory

    **Returns**:
    - The mutated keyword arguments of the executed function.

    **Example**:
    ```
    async def update_user_info(user_id, name=None, email=None):
        # code to update user info in the database
        return {'name': name, 'email': email}

    updated_values = await perpetuate(
        update_user_info, args=[123], memory={'name': 'John'}
    )
    # updated_values will be {'name': 'John', 'email': None}
    # (assuming the original value of email was None)
    ```
    """
    update = await autofill(function, args=args, memory=memory)
    if isinstance(update, dict):
        memory.update(update)
        logging.debug(
            "Mutation = %s", json.dumps(update, indent=4, default=lambda a: str(a))
        )
        # logging.debug('Memory = %s', json.dumps(memory, indent=4, default=lambda a: str(a)))
        for key, value in update.items():
            if key in ONS:
                for condition, func, singularize in ONS[key]:
                    if singularize:
                        if not isinstance(value, Iterable):
                            raise ValueError(
                                "Singularize received a non iterable value"
                            )
                        await asyncio.gather(
                            *[
                                autofill(func, args=[iterated], memory=memory)
                                for iterated in value
                            ]
                        )
                    else:
                        if (
                            condition
                            and await autofill(condition, args=[value], memory=memory)
                        ) or not condition:
                            await autofill(func, args=[value], memory=memory)
    return update
