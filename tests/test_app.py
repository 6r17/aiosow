
import os
import pytest
from aiohttp import web
from unittest import mock
from stims.app import app_factory

async def mock_initialize(app, mem):
    app['mem'] = mem

@mock.patch('stims.setup.initialize', new=mock_initialize)
@pytest.mark.asyncio
async def test_app_factory():
    os.environ['VAR1'] = 'value1'
    os.environ['VAR2'] = 'value2'
    app = await app_factory()
    assert isinstance(app, web.Application)
    assert app['mem']['VAR1'] == 'value1'
    assert app['mem']['VAR2'] == 'value2'
