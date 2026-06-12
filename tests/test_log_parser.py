from tarkov_tool.tarkov.log import LogParser

from pathlib import Path
import tomllib
_test_log_paths = Path(__file__).parent / 'test_log_paths.toml'
_paths:list[str] = tomllib.load(_test_log_paths.open("rb")).get('logs',[])


class Test:...