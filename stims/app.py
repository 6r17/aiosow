import os, importlib
from aiohttp import web

async def app_factory():
    app = web.Application()
    mem = os.environ.copy()
    mod = importlib.import_module("stims.setup")
    await mod.initialize(app, mem)
    return app
