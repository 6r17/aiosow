
import pytest, warnings, subprocess

@pytest.mark.asyncio
async def test_run():
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        result = subprocess.run(['stims', 'stims.routine', '-d', '--no_run_forever'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        assert result.returncode == 0
