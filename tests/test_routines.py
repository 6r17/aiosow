import pytest
from aiosow.routines import routine, clear_routines, get_routines, consume_routines


@pytest.fixture(autouse=True)
def do_clear_routines():
    clear_routines()


def test_routine_decorator():
    @routine(5, perpetuate=False)
    def my_function():
        print("Hello world!")

    assert len(get_routines()) == 1
    assert get_routines()[0]["function"] == my_function
    assert get_routines()[0]["timeout"] == 5
    assert get_routines()[0]["perpetuate"] == False


@pytest.mark.asyncio
async def test_consume_routines_empty():
    await consume_routines(memory={})
