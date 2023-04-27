import pytest
from aiosow.routines import (
    routine,
    clear_routines,
    get_routines,
    consume_routines,
    infinite_generator,
)


@pytest.fixture(autouse=True)
def do_clear_routines():
    clear_routines()


@pytest.mark.asyncio
async def test_routine_decorator():
    @routine(0.2, perpetuate=False)
    def my_function():
        return {"test": "test"}

    memory = {}
    assert len(get_routines()) == 1
    assert get_routines()[0]["function"] == my_function
    assert get_routines()[0]["timeout"] == 0.2
    assert get_routines()[0]["perpetuate"] == False
    await consume_routines(memory=memory)
    assert memory.get("test", None) == None


@pytest.mark.asyncio
async def test_consume_routines_empty():
    def my_function():
        return {"test": "test"}

    routine(0.2)(my_function)
    memory = {}
    await consume_routines(memory=memory)
    assert memory["test"] == "test"


@pytest.mark.asyncio
async def test_routines_should_raise_if_raise_true():
    def my_function():
        raise ValueError

    routine(0.1)(my_function)
    assert len(get_routines()) == 1
    memory = {"raise": True}
    with pytest.raises(Exception):
        await consume_routines(memory=memory)
    memory = {"raise": False}
    await consume_routines(memory=memory)


@pytest.mark.asyncio
async def test_routines_should_be_removed_with_negative_frequency():
    def my_function():
        raise ValueError

    memory = {}
    routine(-0.1)(my_function)
    assert len(get_routines()) == 1
    await consume_routines(memory=memory)
    assert len(get_routines()) == 0


async def test_infinite_generator():
    async def my_condition():
        return True

    async def my_function():
        yield 1
        yield 2

    generator_consumer = infinite_generator(my_condition)(my_function)

    assert await generator_consumer() == 1
    assert await generator_consumer() == 2
    assert await generator_consumer() == 1
