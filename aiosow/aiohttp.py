"""
# aioHTTP
[![](https://img.shields.io/pypi/v/aiohttp?color=white&style=for-the-badge)](https://pypi.org/project/aiohttp/)
[![](https://img.shields.io/github/stars/aio-libs/aiohttp?color=white&logo=github&style=for-the-badge)](https://github.com/aio-libs/aiohttp)

`aiohttp` is an asynchronous HTTP client/server framework for Python.
It provides a client and server API for making HTTP requests and 
handling HTTP responses, supporting features such as HTTP/1.x and HTTP/2,
SSL/TLS encryption, cookies, and WebSockets. 
`aiohttp`'s server API is built on top of `asyncio`, allowing it to handle a large 
number of concurrent requests efficiently. It also provides support for routing 
and middleware, allowing developers to easily define complex request handling logic. 

# Getting started
- [Quickstart](https://docs.aiohttp.org/en/stable/client_quickstart.html)
- [Examples](https://aiohttp-demos.readthedocs.io/en/latest/index.html#aiohttp-demos-polls-beginning)

# Installation

Even tough this module is available on the base package, aiohttp is an optional
dependency and needs to be installed

```
pip3 install aiohttp
```

# Usage

"""


from aiohttp import web
from aiosow.setup import setup

routes = web.RouteTableDef()

@setup
async def aiohttp_server() -> None:
    """Set up and start an aiohttp server with the specified routes."""
    global routes
    app = web.Application()
    app.add_routes(routes) 
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    return site.start()

__all__ = ['routes']
