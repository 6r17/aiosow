
from unittest.mock import Mock
import pytest

from stims.wire import wire

@pytest.mark.asyncio
async def test_wire_triggers_listeners():
    mock_listener = Mock()
    trigger_decorator, listen_decorator = wire()
    listen_decorator(mock_listener)
    await trigger_decorator(lambda: 1)()
    assert mock_listener.call_count == 1
