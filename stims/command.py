#! env python3.11

import logging, importlib, asyncio
import click

from stims import routines
from stims.setup import initialize
from stims.run import do_run

async def init_and_run(kwargs):
    await initialize(kwargs)
    await do_run(kwargs)

@click.command()
@click.argument('path')
@click.option('-c', '--config', help='Path to configuration file', show_default=True)
@click.option('-d', '--debug', default=False, is_flag=True, help='Debug mode', show_default=True)
@click.pass_context
def run(*__args__, **kwargs):
    logging.basicConfig(level=logging.DEBUG if kwargs.get('debug') else logging.INFO)
    logging.debug("kwargs = %s", kwargs)
    asyncio.run(init_and_run(kwargs))

if __name__ == '__main__':
    run() # pragma: no cover
