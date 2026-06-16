from .tarkov.path import logs_folder, screenshots_folder
from .event_manger import EventManger
from .events import TARKOV_START, TARKOV_STOP, TARKOV_SCREENSHOT
from .tarkov.log import LogParser

import time
import threading
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogWatcher(FileSystemEventHandler):
    # on_modified can't get Tarkov Game log write
    __slots__ = ('watch_dir', 'pattern', 'interval', 'observer',
                 'tracked_files', 'tracked_dir', '_stop_event', '_thread','log_parsers')
    def __init__(self, watch_dir:Path=None, interval=5):
        if watch_dir is None:
            watch_dir = logs_folder()
        if watch_dir is None:
            return ValueError('can\'t find log dir')
        self.watch_dir = watch_dir
        self.log_parsers:list[LogParser] = []
        self.interval = interval
        self.observer = Observer()
        self.tracked_files:dict[Path,int] = {}
        self.tracked_dir:list[Path] = []
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._poll_logs_loop)

    def on_created(self, event):
        if event.is_directory:
            self.tracked_dir.append(Path(event.src_path))
        # p = Path(event.src_path)
        # if p.match('*.log'):
        #     print(f'偵測到新日誌檔案: {p}')
        #     self.tracked_files[p] = 0

    def start(self):
        self.observer.schedule(self, str(self.watch_dir), recursive=True)
        self.observer.start()
        self._thread.start()
        print(f'開始監控資料夾: {self.watch_dir}')

    def stop(self):
        self._stop_event.set()
        self.observer.stop()
        self.observer.join()
        self._thread.join()
        print('監控已停止')

    def _poll_logs(self):
        for log in self.tracked_files.keys():
            if log.exists():
                try:
                    with log.open('r', encoding='utf-8') as logf:
                        logf.seek(self.tracked_files[log])
                        new_content = logf.read()
                        if new_content:
                            print(f'[{log.name}] 新增內容:\n{new_content}')
                            self.tracked_files[log] = logf.tell()
                except Exception as e:
                    print(f'讀取失敗: {e}')

    def _poll_logs_loop(self):
        while not self._stop_event.is_set():
            time.sleep(self.interval)
            if self.tracked_dir:
                self._poll_logs()
                self.tracked_files.clear()
                
                continue
            self._poll_logs()

class ScreenshotWatcher(FileSystemEventHandler):
    from .tarkov.screenshot import get_screenshot_info
    get_screenshot_info = staticmethod(get_screenshot_info)
    __slots__ = ('folder','observer')
    _inited = False
    def __init__(self, watch_dir:Path=None):
        if self._inited:
            raise RuntimeError('screenshot watcher only init one time')
        self._inited = True
        if watch_dir is None:
            watch_dir = screenshots_folder()
        if watch_dir is None:
            return ValueError('can\'t find screenshots dir')
        self.folder = watch_dir
        self.observer = Observer()

    def on_created(self, event):
        if event.is_directory:
            return
        p = Path(event.src_path)
        if p.match('*.png'):
            e = TARKOV_SCREENSHOT(info=self.get_screenshot_info(p))
            EventManger._trigger(e)

    def start(self):
        self.observer.schedule(self, str(self.folder), recursive=True)
        self.observer.start()
        print(f'開始監控資料夾: {self.folder}')

    def stop(self):
        # self._stop_event.set()
        self.observer.stop()
        self.observer.join()
        print('監控已停止')

class TarkovWatcher:
    ''