import pytest
from aiohttp import web
from stims.aiohttp import app_factory

@pytest.mark.asyncio
async def test_app_factory():
    app = await app_factory()
    assert isinstance(app, web.Application)
