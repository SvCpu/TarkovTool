from functools import lru_cache
from pathlib import Path
import winreg
import os
from contextlib import suppress
import ctypes.wintypes

@lru_cache(maxsize=1)
def install_path() -> Path|None:
    install_location = None
    with suppress():
        registry_path = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\EscapeFromTarkov"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
            install_location, _ = winreg.QueryValueEx(key, "InstallLocation")
    with suppress(Exception):
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 3932890"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
            install_location, _ = winreg.QueryValueEx(key, "InstallLocation")
    return Path(install_location) if install_location else None

@lru_cache(maxsize=1)
def logs_folder() -> Path|None:
    '''獲取塔科夫日誌資料夾路徑

    Returns:
        Path|None: 日誌資料夾路徑
    '''
    if install_location:= install_path():
        return Path(install_location) / 'Logs'
    return None

@lru_cache(maxsize=1)
def screenshots_folder() -> Path|None:
    '''獲取塔科夫截圖資料夾路徑

    Returns:
        Path|None: 截圖資料夾路徑
    '''

    CSIDL_PERSONAL = 5
    SHGFP_TYPE_CURRENT = 0

    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

    documents_path = Path(buf.value)
    if documents_path.exists():
        default = documents_path / "Escape From Tarkov" / "Screenshots"
        return default if default.exists() else None

@lru_cache(maxsize=1)
def temp_folder() -> Path|None:
    temp_dir = os.getenv("TEMP")
    temp_path = Path(temp_dir) / "Battlestate Games" / "EscapeFromTarkov"
    if temp_path.exists():
        return temp_path