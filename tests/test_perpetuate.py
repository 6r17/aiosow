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
    mem = { 'a': 1, 'b': [] }
    mock = mocker.Mock()
    mockb = mocker.Mock()
    on('a')(mock)
    on('b', singularize=True)(mockb)
    assert await perpetuate(lambda: { 'a': 2 }, kwargs=mem)
    mock.assert_called_once()
    assert await perpetuate(lambda: { 'b': [1, 2] }, kwargs=mem)
    assert mockb.call_count == 2
    with pytest.raises(ValueError):
        await perpetuate(lambda: { 'b': 1 }, kwargs=mem)
