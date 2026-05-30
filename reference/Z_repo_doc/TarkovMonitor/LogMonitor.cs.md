# LogMonitor.cs

非同步日誌輪詢模組，對單一日誌檔案進行增量讀取。

## 流程

```
Start()
  └─ 非 Application 型：fileBytesRead = 檔案當前大小（跳過既有內容）
  └─ while(true) 每 5 秒輪詢：
       ├─ 檢查檔案大小 change
       │    ├─ 無變化 → sleep
       │    └─ 有增長 → 從 fileBytesRead 位置開始讀取新增位元組
       │         ├─ 每次讀取最多 1024 bytes，合併為 chunks
       │         └─ 觸發 NewLogData 事件（傳遞合併後的 UTF-8 字串）
       └─ fileBytesRead += newBytesRead
  └─ Stop() → cancel = true 跳出迴圈
```

## 核心欄位

| 欄位 | 型別 | 說明 |
|---|---|---|
| `Path` | `string` | 監控的日誌檔案完整路徑 |
| `Type` | `GameLogType` | 日誌型別（Application / Notifications / Traces） |
| `fileBytesRead` | `long` | 已讀取的位元組數（用於計算增量） |
| `cancel` | `bool` | 停止信號 |
| `MaxBufferLength` | `int` | 每次讀取緩衝大小，固定 1024 bytes |

## 事件

| 事件 | 觸發時機 |
|---|---|
| `InitialReadComplete` | 初次讀取完成（非 Application 型在取得初始大小後立即觸發；Application 型在第一次新資料讀取完成後觸發） |
| `NewLogData` | 有新日誌資料時，傳遞 `NewLogDataEventArgs`（含 Type、Data、InitialRead 旗標） |
| `Exception` | 讀取過程中發生例外時 |

## 關鍵設計

- **FileShare.ReadWrite**：使用 `FileShare.ReadWrite` 開啟檔案，避免鎖定正在被遊戲寫入的日誌
- **非 Application 跳過初始內容**：遊戲啟動時日誌已存在大量歷史資料，非 Application 型日誌直接將 `fileBytesRead` 設為當前檔案大小，僅監控後續新行
- **UTF-8 解碼**：區塊合併後以 `Encoding.UTF8.GetString()` 解碼（不保證行邊界對齊，由呼叫端自行拆行解析）

## Python 等效實作

```python
import os
import time
from threading import Event, Thread
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class LogData:
    text: str
    is_initial: bool

class LogMonitor:
    def __init__(self, path: str, skip_existing: bool = True, 
                 on_new_data: Optional[Callable[[LogData], None]] = None):
        self.path = path
        self.skip_existing = skip_existing
        self.on_new_data = on_new_data
        self._stop = Event()
        self._thread: Optional[Thread] = None

    def start(self):
        self._thread = Thread(target=self._poll, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=10)

    def _poll(self):
        file_bytes_read = os.path.getsize(self.path) if self.skip_existing else 0

        while not self._stop.is_set():
            try:
                size = os.path.getsize(self.path)
                if size > file_bytes_read:
                    with open(self.path, "r", encoding="utf-8", errors="replace") as f:
                        f.seek(file_bytes_read)
                        new_data = f.read()
                    
                    if self.on_new_data:
                        self.on_new_data(LogData(
                            text=new_data,
                            is_initial=file_bytes_read == 0
                        ))
                    file_bytes_read = size
            except OSError:
                pass
            
            time.sleep(5)
```
