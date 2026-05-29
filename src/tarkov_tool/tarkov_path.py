from pathlib import Path
import winreg
import os
from contextlib import suppress

def get_tarkov_install_path() -> Path|None:
    install_location = None
    with suppress():
        registry_path = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\EscapeFromTarkov"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
            install_location, _ = winreg.QueryValueEx(key, "InstallLocation")
    with suppress():
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 3932890"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
            install_location, _ = winreg.QueryValueEx(key, "InstallLocation")
    return Path(install_location) if install_location else None

def get_default_logs_folder() -> Path|None:
    '''獲取塔科夫日誌資料夾路徑

    Returns:
        Path|None: 日誌資料夾路徑
    '''
    if install_location:= get_tarkov_install_path():
        return Path(install_location) / 'Logs'
    return None

def get_default_screenshots_folder() -> Path|None:
    '''獲取塔科夫截圖資料夾路徑

    Returns:
        Path|None: 截圖資料夾路徑
    '''
    default = Path.home() / "Documents"/ "Escape From Tarkov" / "Screenshots"
    return default if default.exists() else None

def get_default_tarkov_temp_folder() -> Path|None:
    temp_dir = os.getenv("TEMP")
    temp_path = Path(temp_dir) / "Battlestate Games" / "EscapeFromTarkov"
    if temp_path.exists():
        return temp_path