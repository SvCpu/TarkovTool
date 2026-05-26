import pytest
from unittest.mock import Mock

@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    yield

class TestEventTrigger:
    from tarkov_tool.event_manger import EventManger
    from tarkov_tool.events import ON_STARTUP, ON_SHUTDOWN
    def test_event_on_statup(self):
        mock_handler = Mock()
        self.EventManger.register(event=self.ON_STARTUP, handler=mock_handler)
        self.EventManger.Enable()
        mock_handler.assert_called_once()
    def test_event_on_shutdown(self):
        mock_handler = Mock()
        self.EventManger.register(event=self.ON_SHUTDOWN, handler=mock_handler)
        self.EventManger.Disable()
        mock_handler.assert_called_once()