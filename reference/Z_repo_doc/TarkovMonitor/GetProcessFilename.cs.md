# GetProcessFilename.cs

透過 Windows API 從 **32 位元行程**取得完整執行檔路徑的工具類別。

## 背景

TarkovMonitor 本身是 **32 位元**編譯（`x86`），因此在 64 位元系統上開啟 EFT （64 位元行程）時，無法使用 .NET 標準的 `Process.MainModule.FileName`（會拋出 `Win32Exception`）。此類別繞過這個限制，直接 P/Invoke kernel32 原生 API。

## 流程

1. `OpenProcess(QueryLimitedInformation, false, processId)` → 取得行程控制代碼
2. `QueryFullProcessImageName(hProcess, 0, StringBuilder, ref capacity)` → 取得完整路徑
3. 回傳 `builder.ToString()`（失敗回傳空字串）

## 使用的 Win32 API

| API | DLL | 功能 |
|---|---|---|
| `OpenProcess` | kernel32.dll | 用 `QueryLimitedInformation` (0x1000) 權限開啟指定 PID 的行程控制代碼 |
| `QueryFullProcessImageName` | kernel32.dll | 從行程控制代碼讀取完整的執行檔路徑 |

## Windows 權限需求

- `QueryLimitedInformation` 不需要 `SeDebugPrivilege`，對目標行程僅需最低的查詢權限
- 正常使用者權限即可運作（不需要管理員身份）

## Python 等效實作

```python
import ctypes
from ctypes import wintypes

def get_process_filename(pid: int) -> str:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h_process:
        return ""
    
    try:
        buf = ctypes.create_unicode_buffer(2000)
        size = wintypes.DWORD(2000)
        if kernel32.QueryFullProcessImageNameW(h_process, 0, buf, ctypes.byref(size)):
            return buf.value
        return ""
    finally:
        kernel32.CloseHandle(h_process)
```
