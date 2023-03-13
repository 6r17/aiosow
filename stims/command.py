#! env python3.11
# pragma: no cover
import os
import json
import site
import configparser

from aiohttp.web import run_app
from aiohttp_devtools.runserver.main import runserver as _runserver

import click

import importlib

def string_from_file(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as _file:
        return ''.join(_file.readlines())

def set_current_dir():
    current_dir = os.path.abspath(os.getcwd())
    os.environ['CURRENT_DIR'] = current_dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

def print_version(ctx, __param__, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('2.0.0')
    ctx.exit()

def get_config_path():
    return site.getsitepackages()[0] + "/exorde_packages.ini"

def install(ctx, __param__, value):
    if not value or ctx.resilient_parsing:
        return
    jason = string_from_file(
        '/'.join(os.path.abspath(__file__).split('/')[:-1]) + '/compositions.json'
    )
    packages = json.loads(jason)
    config = configparser.ConfigParser()
    config.read(get_config_path())
    if not config.has_section('packages'):
        config.add_section('packages')
    if value not in packages:
        print('package not found')
    else:
        click.echo(f'Downloading and installing package "{value}"...')
        os.system(f'pip3.10 install git+{packages[value]}')
        config.set('packages', value, 'installed')
        with open(get_config_path(), 'w') as config_file:
            config.write(config_file)
        click.echo(f'Package "{value}" installed successfully.')
    ctx.exit()

def devinstall(ctx, __param__, value):
    if not value or ctx.resilient_parsing:
        return
    config = configparser.ConfigParser()
    config.read(get_config_path())
    if not config.has_section('packages'):
        config.add_section('packages')
    click.echo(f'Installing package from "{value}"...')
    os.system(f'pip3.10 install -e {value}')
    config.set('packages', value, 'installed')
    with open(get_config_path(), 'w') as config_file:
        config.write(config_file)
    click.echo(f'Package "{value}" installed successfully.')
    ctx.exit()

def list_installed(ctx, __param__, value):
    if not value or ctx.resilient_parsing:
        return
    config = configparser.ConfigParser()
    config.read(get_config_path())
    if not config.has_section("packages"):
        ctx.exit()
    else:
        for pack in config.options("packages"):
            click.echo(f' - {pack}')
    ctx.exit()

@click.command()
@click.option(
    '-c', '--config',
    default=os.path.expanduser('~') + '/.config/exorde-cli/config.yaml',
    help='Path to configuration file', show_default=True
)
@click.option(
    '-comp', '--composition',
    default='/'.join(os.path.abspath(__file__).split('/')[:-1]) + '/composition/',
    help='Name or path of composition to be played',
)
@click.option('-d', '--debug', is_flag=True, default=False, help='Debug mode', show_default=True)
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help='Print version and exit')
@click.option('--install', callback=install, expose_value=False, is_eager=True, help='Install composition')
@click.option('--devinstall', callback=devinstall, expose_value=False, is_eager=True, help='Install composition from a directory, allows live-reload')
@click.option('--list', is_flag=True, callback=list_installed, expose_value=False, is_eager=True, help='List of installed compositions')
@click.pass_context
def run(*__args__, **kwargs):
    ctx = click.get_current_context()
    composition_source = ctx.get_parameter_source('composition')
    if composition_source == click.core.ParameterSource.DEFAULT:
        '''Default selected composition means different storage path'''
    # the following fixes a path restriction caused by aiohttp
    set_current_dir()
    dirpath = os.path.dirname(os.path.abspath(__file__))
    os.environ['params'] = json.dumps(kwargs)
    run_app(**_runserver(**{'app_path': f'{dirpath}/app.py'}))

# this adds options dynamicly depending on installed compositions
config = configparser.ConfigParser()
config.read(get_config_path())
PARAMETERS = {}
if config.has_section("packages"):
    for package in config.options('packages'):
        imported = importlib.import_module(package)
        if hasattr(imported, 'PARAMETERS'):
            for key, value in imported.PARAMETERS.items():
                if not PARAMETERS.get(key, None):
                    PARAMETERS[key] = {}
                PARAMETERS[key].update(value)
    for key, value in PARAMETERS.items():
        run = click.option(f'--{key}', **value)(run)

if __name__ == '__main__':
    run()
