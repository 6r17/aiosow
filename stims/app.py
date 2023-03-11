import logging
import configparser
import importlib
import os
import json
import logging
from aiohttp import web

from stims.command import get_config_path

async def app_factory():
    '''
    App_factory is Used as an entry-point for the reloader.
    - It creates the aiohttp app that is used as a server.
    - It imports the provided composition
    '''
    app = web.Application()
    mem = json.loads(os.environ['params'])
    app.mem = mem
    logging.basicConfig(level=logging.INFO if not mem['debug'] else logging.DEBUG)
    
    config = configparser.ConfigParser()
    config.read(get_config_path())
    if config.has_section("packages"):
        if mem['composition'] in config.options('packages'):
            importlib.import_module(mem['composition'] + '.bindings')
            logging.info('Loaded composition : %s', mem['composition'])
    else:
        print('todo: from path')
    # run_setups is then running those functions, see more in __init__
    bindings = importlib.import_module('exorde.bindings')
    await bindings.initialize(app=app, mem=mem)
    logging.info('start of Exorde-CLI')
    return app
