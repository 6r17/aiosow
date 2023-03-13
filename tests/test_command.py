
import pytest
from unittest import mock

from click.testing import CliRunner

def test_hello_world():
    with mock.patch('aiohttp.web.run_app') as run_app_mock:
        from stims.command import run
        runner = CliRunner()
        runner.invoke(run, ['-d'])
        assert run_app_mock.called_once()
