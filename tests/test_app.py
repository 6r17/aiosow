import os, json
import pytest
from aiohttp import web
from unittest import mock
from stims.app import app_factory

async def mock_initialize(app, mem):
    app['mem'] = mem

@mock.patch('stims.setup.initialize', new=mock_initialize)
@pytest.mark.asyncio
async def test_app_factory():
    os.environ['STIMS_CONFIG'] = json.dumps({"a": "test"})
    app = await app_factory()
    assert isinstance(app, web.Application)
    assert app['mem']['a'] == 'test'
