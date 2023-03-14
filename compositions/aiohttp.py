'''
[AIOHTTP](https://docs.aiohttp.org/en/stable/) web server implementation.

Asynchronous HTTP Client/Server for [asyncio](https://docs.python.org/3/library/asyncio.html)
and Python.

'''
from aiohttp import web
from aiojobs.aiohttp import setup as aiosetup
from stims.setup import setup

async def handler(__request__):
    return web.Response()

@setup
def aiohttp_factory():
    app = web.Application()
    app.router.add_get('/', handler)
    aiosetup(app)
