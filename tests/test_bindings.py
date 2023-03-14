
import time
import pytest
from stims.bindings import delay, wrap, each

from typing import Callable



@pytest.fixture
def synchronous_function():
    def my_synchronous_function():
        return True
    return my_synchronous_function

@pytest.fixture
def asynchronous_function():
    async def my_asynchronous_function():
        return True
    return my_asynchronous_function

@pytest.mark.asyncio
async def test_delay_decorator(synchronous_function, asynchronous_function):
    delayed_synchronous = delay(seconds=0.005)(synchronous_function)
    start_time = time.monotonic()
    result = await delayed_synchronous()
    end_time = time.monotonic()
    assert result is True
    assert end_time - start_time >= 0.005  # Ensure delay of at least 0.005 seconds

    delayed_asynchronous = delay(seconds=0.005)(asynchronous_function)
    start_time = time.monotonic()
    result = await delayed_asynchronous()
    end_time = time.monotonic()
    assert result is True
    assert end_time - start_time >= 0.005  # Ensure asynchronous function has same behavior

@pytest.mark.asyncio
async def test_wrapper_decorator():
    assert await wrap(lambda a: { "test": a })(lambda : 2)() == { "test": 2 }


@pytest.mark.asyncio
async def test_each_decorator():
    async def count():
        for i in range(3):
            yield i

    async def square(n):
        return n * n

    assert await each(count)(square)() == [0, 1, 4]
