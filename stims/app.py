import logging
import os, importlib, json
from aiohttp import web

async def app_factory():
    mem = json.loads(os.environ['STIMS_CONFIG'])
    logging.basicConfig(level=logging.DEBUG if mem.get('debug') else logging.INFO)
    logging.debug("mem = %s", mem)
    app = web.Application()
    mod = importlib.import_module("stims.setup")
    await mod.initialize(app, mem)
    return app
