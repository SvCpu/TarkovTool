from tarkov_tool.tarkov import path

from pathlib import Path

def test_install_folder_type():
    result = path.install_folder()
    assert result is None or isinstance(result, Path)

def test_logs_folder_type():
    result = path.logs_folder()
    assert result is None or isinstance(result, Path)

def test_screenshots_folder_type():
    result = path.screenshots_folder()
    assert result is None or isinstance(result, Path)

def test_temp_folder_type():
    result = path.temp_folder()
    assert result is None or isinstance(result, Path)
