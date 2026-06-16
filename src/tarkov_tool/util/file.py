import time
import threading
from pathlib import Path

class FileDeleter:
    @classmethod
    def delete_files(cls, targets: list[Path], retry_interval: float = 1.0, max_attempts: int = 10) -> None:
        def worker():
            remaining = set(targets)
            attempts = {path: 0 for path in remaining}
            while remaining:
                for path in list(remaining):
                    try:
                        if path.exists():
                            path.unlink()
                        remaining.remove(path)
                        attempts.pop(path, None)
                    except (PermissionError, OSError):
                        attempts[path] += 1
                        if attempts[path] >= max_attempts:
                            remaining.remove(path)
                            attempts.pop(path, None)
                if remaining:
                    time.sleep(retry_interval)
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
