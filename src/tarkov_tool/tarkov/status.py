import time
import psutil
import threading
import ctypes
import ctypes.wintypes
import win32gui
import win32con
import pythoncom

class TarkovWindowMonitor:
    '''塔科夫視窗監控器
    動態提供當前狀態
    '''
    def __init__(self):
        self._is_visible = False
        self._hwnd = None
        self._lock = threading.Lock()
        self._hook = None
        self._running = False
        self._target_title = "EscapeFromTarkov"

        self._WinEventProcType = ctypes.WINFUNCTYPE(None,ctypes.wintypes.HANDLE,ctypes.wintypes.DWORD,ctypes.wintypes.HWND,ctypes.wintypes.LONG,ctypes.wintypes.LONG,ctypes.wintypes.DWORD,ctypes.wintypes.DWORD)
        self._event_callback_func = self._WinEventProcType(self._event_callback)

    def _find_window(self):
        def callback(hwnd, found):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if self._target_title in title:
                    found.append(hwnd)
        result = []
        win32gui.EnumWindows(callback, result)
        return result[0] if result else None

    def _event_callback(self, hWinEventHook, event, hwnd_event, idObject, idChild, dwEventThread, dwmsEventTime):
        with self._lock:
            if hwnd_event == self._hwnd:
                self._is_visible = False
                self._hwnd = None
                if self._hook:
                    ctypes.windll.user32.UnhookWinEvent(self._hook)
                    self._hook = None

    def _monitor_loop(self):
        self._running = True
        while self._running:
            hwnd = self._find_window()
            with self._lock:
                self._hwnd = hwnd
                self._is_visible = bool(hwnd and win32gui.IsWindowVisible(hwnd))
                if hwnd and not self._hook:
                    self._hook = ctypes.windll.user32.SetWinEventHook(win32con.EVENT_OBJECT_DESTROY,win32con.EVENT_OBJECT_DESTROY,0,self._event_callback_func,0, 0,win32con.WINEVENT_OUTOFCONTEXT)
            pythoncom.PumpWaitingMessages()
            time.sleep(0.1)

    def start(self):
        '開啟監控'
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()

    def stop(self):
        '停止監控'
        with self._lock:
            self._running = False
            if self._hook:
                ctypes.windll.user32.UnhookWinEvent(self._hook)
                self._hook = None

    @property
    def is_visible(self) -> bool:
        '是否存在塔科夫窗口'
        with self._lock:
            return self._is_visible

    @property
    def is_foreground(self) -> bool:
        '塔科夫窗口是否在最上層'
        with self._lock:
            return self._hwnd and win32gui.GetForegroundWindow() == self._hwnd

def is_tarkov_window_active() -> bool:
    '此方法僅根據標題判斷塔科夫是否運行'
    def callback(hwnd, found):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "EscapeFromTarkov" in title:
                found.append(True)
    result = []
    win32gui.EnumWindows(callback, result)
    return bool(result)

def is_tarkov_running() -> bool:
    return any(
        p.info["name"] == "EscapeFromTarkov.exe"
        for p in psutil.process_iter(["name"])
    )

# def is_tarkov_running() -> bool:
#     '''根據進程名稱判斷塔科夫是否運行

#     Returns:
#         bool: is not running
#     '''
#     for proc in psutil.process_iter():
#         try:
#             if proc.name() == "EscapeFromTarkov.exe":
#                 return True
#         except (psutil.NoSuchProcess, psutil.AccessDenied):
#             continue
#     return False