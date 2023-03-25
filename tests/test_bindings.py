import time
import pytest
from aiosow.bindings import delay, wrap, each, wire, accumulator, read_only, debug

from unittest.mock import Mock


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
async def test_wire_triggers_listeners():
    mock_listener = Mock()
    mock_listener.__name__ = "mock"
    trigger_decorator, listen_decorator = wire()
    listen_decorator(mock_listener)
    await trigger_decorator(lambda: 1)()
    assert mock_listener.call_count == 1


@pytest.mark.asyncio
async def test_wire_triggers_with_generator():
    mock_listener = Mock()
    mock_listener.__name__ = "mock"
    trigger_decorator, listen_decorator = wire()
    listen_decorator(mock_listener)

    def generator():
        for i in range(3):
            yield i

    await trigger_decorator(generator)()
    assert mock_listener.call_count == 3


@pytest.mark.asyncio
async def test_wire_chain():
    mock_start = Mock()
    mock_start.__name__ = "mock-start"
    mock_end = Mock()
    mock_end.__name__ = "mock-end"
    a_trigger_on, a_on_trigger_do = wire()
    b_trigger_on, b_on_trigger_do = wire()

    trigger = a_trigger_on(mock_start)
    value_trigger = a_trigger_on(lambda value: value)

    a_on_trigger_do(b_trigger_on(lambda value: value))
    b_on_trigger_do(mock_end)

    await trigger()
    assert mock_start.call_count == 1
    assert mock_end.call_count == 1

    await value_trigger(2)
    assert mock_end.call_count == 2
    mock_end.assert_called_with(2)


@pytest.mark.asyncio
async def test_accumulator():
    mock_listener = Mock()
    mock_listener.__name__ = "mock"
    batched = accumulator(2)(mock_listener)
    await batched(1)
    assert mock_listener.call_count == 0
    await batched(2)
    assert mock_listener.call_count == 1


@pytest.mark.asyncio
async def test_accumulator_from_mem():
    mock_listener = Mock()
    mock_listener.__name__ = "mock"
    batched = accumulator(lambda memory: memory["size"])(mock_listener)
    await batched(1, memory={"size": 2})
    assert mock_listener.call_count == 0
    await batched(2, memory={"size": 2})
    assert mock_listener.call_count == 1


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
    assert (
        end_time - start_time >= 0.005
    )  # Ensure asynchronous function has same behavior


@pytest.mark.asyncio
async def test_wrapper_decorator():
    assert await wrap(lambda a: {"test": a})(lambda: 2)() == {"test": 2}


@pytest.mark.asyncio
async def test_each_decorator():
    async def count():
        for i in range(3):
            yield i

    async def square(n):
        return n * n

    assert await each(count)(square)() == [0, 1, 4]


@pytest.mark.asyncio
async def test_each_without_argument():
    """This test each withtout any transformation"""

    async def square(n):
        return n * n

    assert await each()(square)([0, 1, 2]) == [0, 1, 4]


@pytest.mark.asyncio
async def test_read_only():
    getter = read_only(42)
    assert getter() == 42


@pytest.mark.asyncio
async def test_debug():
    mock_listener = Mock()
    mock_listener.__name__ = "trigger"

    @debug(mock_listener)
    async def raises():
        raise Exception("error")

    await raises()
    assert mock_listener.call_count == 1
