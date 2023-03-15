"""
`aiohttp` is an asynchronous HTTP client/server framework for Python.
It provides a client and server API for making HTTP requests and 
handling HTTP responses, supporting features such as HTTP/1.x and HTTP/2,
SSL/TLS encryption, cookies, and WebSockets. 
Aiohttp's server API is built on top of asyncio, allowing it to handle a large 
number of concurrent requests efficiently. It also provides support for routing 
and middleware, allowing developers to easily define complex request handling logic. 

# Getting started
- [Official website](https://docs.aiohttp.org/en/stable/index.html)
- [GitHub repository](https://github.com/aio-libs/aiohttp)
- [Quickstart](https://docs.aiohttp.org/en/stable/client_quickstart.html)
- [Aiohttp Examples](https://aiohttp-demos.readthedocs.io/en/latest/index.html#aiohttp-demos-polls-beginning)

# Installation

Even tough this module is available on the base package, aiohttp is an optional
dependency and need to be installed

```
pip3 install aiohttp
```

# Usage

"""


from aiohttp import web
from stims.setup import setup

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
