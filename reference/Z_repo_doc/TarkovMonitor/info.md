# TarkovMonitor

逃離塔科夫伴侶應用程式。

提供多種實用功能：
- 音頻通知（匹配成功、撤離開始等）
- Goon 追蹤報告
- 自動在 tarkov.dev 網站載入當前地圖
- 透過 API 自動標記 Tarkov Tracker 任務進度
- 本地統計數據追蹤

# log parse
```
reference\TarkovMonitor\TarkovMonitor\GameWatcher.cs
```
## 監控的日誌檔案

| 檔案名稱 | GameLogType | 說明 |
|---|---|---|
| `application.log` / `application_000.log` | `Application` | 主要遊戲日誌，包含地圖載入、配對、遊戲狀態等 |
| `notifications.log` / `notifications_000.log` | `Notifications` | 遊戲內通知，包含組隊、聊天、跳蚤市場、任務狀態等 |
| `traces.log` / `traces_000.log` | `Traces` | 追蹤日誌（目前未使用，被跳過） |

日誌預設存放於 `{EFT安裝目錄}/Logs/` 或 `{EFT安裝目錄}/build/Logs/`，每場遊戲連線會建立一個 `log_yyyy.MM.dd_H-mm-ss/` 資料夾。

## 日誌格式

正則表達式解析每行：
```
(?<date>^\d{4}-\d{2}-\d{2}) (?<time>\d{2}:\d{2}:\d{2}\.\d{3})(?<tzoffset> [+-]\d{2}:\d{2})?\|(?<message>.+$)\s*(?<json>^{[\s\S]+?^}})?
```
- date/time：時間戳
- message：純文字訊息
- json：附帶的 JSON 負載（可選，跨行匹配）

## 監控內容與觸發事件

### 使用者設定檔

| 日誌內容 (message) | 觸發事件 | 說明 |
|---|---|---|
| `Session mode: {mode}` | 設定 `CurrentProfile.Type` | 辨識 PvE / Regular 模式 |
| `SelectProfile ProfileId:{id} AccountId:{acct}` | `ProfileChanged` | 切換使用者設定檔（非初次讀取時） |
| `SelectedProfile ProfileId:{id} AccountId:{acct}` | `ProfileChanged` | 同上（新版訊息） |

### 控制設定

| 日誌內容 (message) | 觸發事件 | 說明 |
|---|---|---|
| `Control settings:` | `ControlSettings` | 讀取遊戲控制設定（JSON 格式） |

### 組隊

| 日誌內容 (message) | 觸發事件 | JSON 解析型別 |
|---|---|---|
| `Got notification \| GroupMatchInviteAccept` | `GroupInviteAccept` | `GroupLogContent` |
| `Got notification \| GroupMatchUserLeave` | `GroupUserLeave` | `GroupMatchUserLeaveLogContent` |
| `Got notification \| GroupMatchWasRemoved` | `GroupDisbanded` | 無 |
| `Got notification \| GroupMatchRaidSettings` | `GroupRaidSettings` | `GroupRaidSettingsLogContent` |
| `Got notification \| GroupMatchRaidReady` | `GroupMemberReady` | `GroupMatchRaidReadyLogContent` |

### 地圖載入與配對

| 日誌內容 (message) | 觸發事件 | 說明 |
|---|---|---|
| `application\|scene preset path:maps/{bundle}.bundle` | `MapLoading` | 地圖開始載入，比對 `MapBundles` 字典（如 `customs_preset` → `bigmap`） |
| `application\|LocationLoaded` | 設定 `raidInfo.MapLoadTime` | 地圖載入完成，正在搜尋配對 |
| `application\|MatchingCompleted` | 設定 `raidInfo.QueueTime` | 配對完成（僅首次進入 RAID，重新連線不觸發） |
| `application\|TRACE-NetworkGameCreate profileStatus` | `MatchFound` / `MapLoaded` / `MapLoading` | 解析地圖名稱、Online/Offline、RaidId；若已連線過設為 `Reconnected`；有排隊且非重新連線時觸發 `MatchFound` |
| `application\|GameStarting` | `RaidStarting` | PMC 倒數開始（Scav 不一定觸發） |
| `application\|GameStarted` | `RaidStarted` | 正式進入 RAID |
| `application\|Network game matching aborted` | `MatchingAborted` | 取消配對 |
| `application\|Network game matching cancelled` | `MatchingAborted` | 同上 |
| `Got notification \| UserMatchOver` | `RaidExited` | RAID 結束，解析 JSON 中的 `location` 和 `shortId` |
| `application\|Init: pstrGameVersion:` | `ExitedPostRaidMenus` | 返回主選單（清理 raidInfo） |

### 聊天與跳蚤市場

| 日誌內容 (message) | 過濾條件 | 觸發事件 | JSON 解析型別 |
|---|---|---|---|
| `Got notification \| ChatMessageReceived` | `type == FleaMarket` + `templateId == "5bdabfb886f7743e152e867e 0"` | `FleaSold` | `FleaSoldMessageLogContent` |
| 同上 | `type == FleaMarket` + `templateId == "5bdabfe486f7743e1665df6e 0"` | `FleaOfferExpired` | `FleaExpiredMessageLogContent` |
| 同上 | `PlayerMessage` | 跳過（忽略玩家聊天訊息） | - |

### 任務

| 日誌內容 (message) | 條件 | 觸發事件 | JSON 解析型別 |
|---|---|---|---|
| `Got notification \| ChatMessageReceived` | `type` 在 `TaskStarted(10)` ~ `TaskFinished(12)` 之間 | `TaskModified` + 依 Status 分別觸發 | `TaskStatusMessageLogContent` |
| | `Status == Started (10)` | `TaskStarted` | |
| | `Status == Failed (11)` | `TaskFailed` | |
| | `Status == Finished (12)` | `TaskFinished` | |

### 螢幕截圖（檔案監控，非日誌）

| 來源 | 檔案名稱格式 | 觸發事件 | 說明 |
|---|---|---|---|
| `FileSystemWatcher` 監控 `Documents/Escape From Tarkov/Screenshots/*.png` | `YYYY-MM-DD[HH-MM]_{x}, {y}, {z}_{rx}, {ry}, {rz}, {rw}_speed.png` | `PlayerPosition` | 正則擷取座標 + 四元數，轉換為 Yaw 角度後觸發 |

## 日誌輪詢機制

`LogMonitor` 每 5 秒檢查日誌檔案大小變化，讀取新增位元組後以 UTF-8 解碼為字串，透過 `NewLogData` 事件傳遞給 `GameWatcher_NewLogData` 處理。非 `Application` 型日誌初次啟動時跳過已有內容（`fileBytesRead` 設為當前檔案大小），僅監控後續新資料。

