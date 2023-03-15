
import pytest, warnings
from click.testing import CliRunner
from stims.command import run

def test_run():
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        runner = CliRunner()
        result = runner.invoke(run, ['stims', '-d', '--no_run_forever'])
        assert result.exit_code == 0
