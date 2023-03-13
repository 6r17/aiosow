import pytest

from stims.perpetuate import perpetuate

@pytest.mark.asyncio
async def test_perpetuate():
    mem = { 'a': 1 }

    def test_function(a):
        return a + 1

    def test_function2(a):
        return { 'result': a + 1 }

    assert await perpetuate(test_function, kwargs=mem) == 2
    assert await perpetuate(test_function2, kwargs=mem) == { 'result': 2 }

    assert mem['result'] == 2
