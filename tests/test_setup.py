import pytest
from stims.setup import initialize, setup, clear_setups

async def my_init_function_1(foo: dict):
    foo['key_1'] = 'value_1'

async def my_init_function_2(foo: dict):
    foo['key_2'] = 'value_2'

@pytest.mark.asyncio
async def test_initialize():
    kwargs = { 'foo': {} }
    clear_setups()
    setup(my_init_function_1)
    setup(my_init_function_2)
    await initialize(kwargs)
    assert kwargs == { 'foo': {'key_1': 'value_1', 'key_2': 'value_2'} }
