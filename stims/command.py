#! env python3.11

import click
import os
import json

from aiohttp.web import run_app
from aiohttp_devtools.runserver.main import runserver as _runserver


@click.command()
@click.option('-c', '--config', help='Path to configuration file', show_default=True)
@click.option('-d', '--debug', default=False, is_flag=True, help='Debug mode', show_default=True)
@click.pass_context
def run(*__args__, **kwargs):
    os.environ['STIMS_CONFIG'] = json.dumps(kwargs)
    run_app(**_runserver(**{'app_path': f'{os.path.dirname(os.path.abspath(__file__))}/app.py'}))

if __name__ == '__main__':
    run() # pragma: no cover
