import aiojobs, pytest
from stims.routines import *
from unittest.mock import AsyncMock, patch

@pytest.fixture(autouse=True)
def do_clear_routines():
    clear_routines()

def test_routine_decorator():
    @routine(interval=5, repeat=False, perpetuate=False)
    def my_function():
        print("Hello world!")

    assert len(get_routines()) == 1
    assert get_routines()[0]["interval"] == 5
    assert get_routines()[0]["function"] == my_function
    assert get_routines()[0]["repeat"] == False
    assert get_routines()[0]["life"] == 0
    assert get_routines()[0]["perpetuate"] == False

@pytest.mark.asyncio
async def test_consume_routines_empty():
    await consume_routines(kwargs={})

@pytest.mark.asyncio
async def test_comsume_routines_with_a_routine():
    routine(interval=1, life=1, repeat=False, perpetuate=True)(lambda a: a)
    routine(interval=1, life=1, repeat=False, perpetuate=False)(lambda a: a)
    routine(interval=1, life=0, repeat=True, perpetuate=False)(lambda a: a)
    routine(interval=1, life=1, repeat=True, perpetuate=False)(lambda a: a)
    await consume_routines(kwargs={})
    assert get_routines()[1]['life'] == 1
