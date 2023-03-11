import pytest
from aiohttp import web
from stims.setup import initialize, setup


@pytest.fixture
def __app__():
    return web.Application()


@pytest.fixture
def mem():
    return {}


@setup
async def my_init_function_1(__app__: web.Application, mem: dict):
    mem['key_1'] = 'value_1'


@setup
async def my_init_function_2(__app__: web.Application, mem: dict):
    mem['key_2'] = 'value_2'
    raise Exception('Oops!')


@pytest.mark.asyncio
async def test_initialize_runs_setup_functions(__app__, mem):
    await initialize(__app__, mem)
    assert mem == {'key_1': 'value_1', 'key_2': 'value_2'}
