import time, asyncio
import pytest
from aiosow.bindings import (
    adapter,
    expect,
    do_raise,
    dont_raise,
    return_true,
    return_false,
    call_limit,
    chain,
    delay,
    wrap,
    each,
    wire,
    accumulator,
    read_only,
    debug,
    make_async,
    until_success,
)

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
async def test_wire_do_unlocks_listeners():
    mock_listener = Mock()
    mock_listener.__name__ = "mock"
    do_unlock_decorator, listen_decorator = wire()
    listen_decorator(mock_listener)
    await do_unlock_decorator(lambda: 1)()
    assert mock_listener.call_count == 1


@pytest.mark.asyncio
async def test_wire_do_unlocks_with_generator():
    mock_listener = Mock()
    mock_listener.__name__ = "mock"
    do_unlock_decorator, listen_decorator = wire()
    listen_decorator(mock_listener)

    def generator():
        for i in range(3):
            yield i

    await do_unlock_decorator(generator)()
    assert mock_listener.call_count == 3


@pytest.mark.asyncio
async def test_wire_chain():
    mock_start = Mock()
    mock_start.__name__ = "mock-start"
    mock_end = Mock()
    mock_end.__name__ = "mock-end"
    a_do_unlock_on, a_on_do_unlock_do = wire()
    b_do_unlock_on, b_on_do_unlock_do = wire()

    do_unlock = a_do_unlock_on(mock_start)
    value_do_unlock = a_do_unlock_on(lambda value: value)

    a_on_do_unlock_do(b_do_unlock_on(lambda value: value))
    b_on_do_unlock_do(mock_end)

    await do_unlock()
    assert mock_start.call_count == 1
    assert mock_end.call_count == 1

    await value_do_unlock(2)
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
    mock_listener.__name__ = "do_unlock"

    @debug(mock_listener)
    async def raises():
        raise Exception("error")

    await raises()
    assert mock_listener.call_count == 1


@pytest.mark.asyncio
async def test_make_async():
    @make_async
    def wait(*__args__):
        time.sleep(0.2)
        return "foo"

    start_time = time.monotonic()
    results = await asyncio.gather(wait(), wait(), wait())
    end_time = time.monotonic()
    assert results == ["foo", "foo", "foo"]
    assert end_time - start_time < (0.3)


@pytest.mark.asyncio
async def test_make_async_parameters():
    @make_async
    def wait(arg):
        return arg * 2

    results = await asyncio.gather(wait(2, memory={}))
    assert results == [4]


@pytest.mark.asyncio
async def test_chain():
    def add(x):
        return x + 1

    def mul(x):
        return x * 2

    def sub(x):
        return x - 3

    def _break(__x__):
        pass

    result = await chain(add, mul, sub)(1)
    # 1 + 1 = 2 ; 2 * 2 = 4 ; 4 - 3 = 1
    assert result == 1
    result = await chain(add, _break)(1)
    assert result == None
    with pytest.raises(Exception):
        result = await chain(add, _break, add)(1)
        assert result == 2


@pytest.mark.asyncio
async def test_until_success():
    attempt = 1

    @until_success()
    async def succeed_on_second_attempt():
        nonlocal attempt
        if attempt == 1:
            attempt += 1
            raise ValueError("fail once")
        else:
            return 42

    result = await succeed_on_second_attempt()
    assert result == 42


@pytest.mark.asyncio
async def test_call_limit():
    @call_limit(1)
    async def increment(x):
        return x + 1

    start_time = time.monotonic()
    result = await increment(0)
    result = await increment(0)
    diff = time.monotonic() - start_time
    assert result == 1
    assert diff >= 1


@pytest.mark.asyncio
async def test_raiser():
    @call_limit(1)
    async def raiser():
        raise ValueError("fail")

    start_time = time.monotonic()
    with pytest.raises(Exception):
        await raiser()
    with pytest.raises(Exception):
        await raiser()
    diff = time.monotonic() - start_time
    assert diff >= 1


def test_return_true():
    assert return_true() == True


def test_return_false():
    assert return_false() == False


def test_do_raise():
    with pytest.raises(ValueError):
        do_raise(ValueError)


from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_expect():
    lock = False

    def unlock(*__args__, **__kwargs__):
        nonlocal lock
        lock = True

    do_unlock = MagicMock(side_effect=unlock)
    dont_unlock = MagicMock()

    async def raise_if_lock_is_false():
        nonlocal lock
        if not lock:
            raise ValueError
        else:
            return lock

    mocked = MagicMock(side_effect=raise_if_lock_is_false)
    patched = expect(do_unlock, retries=2)(mocked)
    result = await patched()
    assert result == True

    lock = False

    with pytest.raises(ValueError):
        mocked = MagicMock(side_effect=raise_if_lock_is_false)
        patched = expect(dont_unlock, retries=1)(mocked)
        result = await patched()

    lock = False
    mocked = MagicMock(side_effect=raise_if_lock_is_false)
    patched = expect(
        dont_unlock, retries=1, on_raise=dont_raise, condition=return_false
    )(mocked)
    result = await patched()


@pytest.mark.asyncio
async def test_adapter():
    async def resolve(item):
        return item + 1

    async def multiply_by_two(num):
        return num * 2

    # Test case 1: Test with a function that takes a single argument
    adapter_func = adapter(resolve)(multiply_by_two)
    result = await adapter_func(1)
    assert result == 4
