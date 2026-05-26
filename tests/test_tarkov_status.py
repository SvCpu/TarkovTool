import pytest

class TestTARKOVStatus:
    from tarkov_tool.tarkov.status import is_tarkov_running
    is_tarkov_running = staticmethod(is_tarkov_running)
    @pytest.fixture
    def game_status(self, request)->bool:
        if request.config.getoption("capture") != "no":
            pytest.skip()
        status = input("請輸入遊戲是否運行 (yes/no): ").strip().lower()
        if status not in ["yes", "no"]:
            raise ValueError("必須輸入 yes 或 no")
        return bool(status == 'yes')
    def test_tarkov_runstatus(self, game_status):
        assert self.is_tarkov_running() == game_status