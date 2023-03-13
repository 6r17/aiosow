import pytest

from stims.perpetuate import perpetuate, on

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

@pytest.mark.asyncio
async def test_on(mocker):
    mem = { 'a': 1 }
    mock = mocker.Mock()
    on('a')(mock)
    assert await perpetuate(lambda: { 'a': 2 }, kwargs=mem)
    mock.assert_called_once()
