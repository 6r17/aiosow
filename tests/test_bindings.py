
import asyncio
import time
import pytest
from stims.bindings import delay

@pytest.mark.asyncio
async def test_delay_decorator():
    async def my_function():
        await asyncio.sleep(1)
        return True

    delayed_func = delay(seconds=2)(my_function)
    start_time = time.monotonic()
    result = await delayed_func()
    end_time = time.monotonic()

    assert result is True
    assert end_time - start_time >= 2  # Ensure delay of at least 2 seconds
