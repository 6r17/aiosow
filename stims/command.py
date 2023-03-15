#! env python3.11

import logging, asyncio, click, importlib
from stims.setup import initialize

@click.command()
@click.argument('path')
@click.option(
    '-c', '--config', help='Path to configuration file', show_default=True
)
@click.option(
    '-d', '--debug', default=False, is_flag=True, help='Debug mode',
    show_default=True
)
@click.option(
    '--no_run_forever', default=False, is_flag=True, help='Wether it should run forever', show_default=True
)
@click.pass_context
def run(*__args__, **kwargs):
    logging.basicConfig(
        level=logging.DEBUG if kwargs.get('debug') else logging.INFO
    )
    logging.debug("kwargs = %s", kwargs)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    importlib.import_module(kwargs['path'])
    tasks = loop.run_until_complete(initialize(kwargs))
    loop.run_until_complete(asyncio.gather(*tasks))
    if not kwargs['no_run_forever']:
        loop.run_forever()

if __name__ == '__main__':
    run() # pragma: no cover
