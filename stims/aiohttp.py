
from aiohttp import web
from stims.setup import setup

async def say_foo(__request__):
    return web.Response(text='Hello, foo!')

@setup
async def aiohttp_server():
    app = web.Application()
    app.add_routes([web.get('/', say_foo)]) 
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    return site.start()
