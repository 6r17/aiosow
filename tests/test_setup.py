import pytest
from aiosow.setup import initialize, setup, clear_setups

async def my_init_function_1(foo: dict):
    foo['key_1'] = 'value_1'

async def my_init_function_2(foo: dict):
    foo['key_2'] = 'value_2'

async def some_task():
    return 'ok'

async def my_init_function_3():
    return some_task()

@pytest.mark.asyncio
async def test_initialize():
    kwargs = { 'foo': {} }
    clear_setups()
    setup(my_init_function_1)
    setup(my_init_function_2)
    setup(my_init_function_3)
    tasks = await initialize(kwargs)
    assert kwargs == { 'foo': {'key_1': 'value_1', 'key_2': 'value_2'} }
    assert len(tasks) == 1
    await tasks[0]
