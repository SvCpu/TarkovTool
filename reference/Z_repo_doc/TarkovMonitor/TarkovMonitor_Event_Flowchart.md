# TarkovMonitor 事件判定流程圖

> 源碼：`reference/TarkovMonitor/TarkovMonitor/GameWatcher.cs`（1110 行）
>
> 核心方法：`GameWatcher_NewLogData()`（328-597 行）

---

## 總體架構

```mermaid
flowchart TD
    Start(["GameWatcher.Start()"])
    --> LogWatch["監控 Logs/ 目錄<br/>FileSystemWatcher"]
    --> WatchFolder["監控最新 log_yyyy.MM.dd_H-mm-ss/ 資料夾"]
    --> CreateMonitors["為 application.log 和<br/>notifications.log 建立 LogMonitor"]
    --> PollLoop["每 5 秒輪詢檔案增量"]
    --> ReadNewData["從上次位置讀取新增位元組<br/>UTF-8 解碼"]
    --> FireNewLogData["觸發 NewLogData 事件"]
    --> ParseLines["GameWatcher_NewLogData()<br/>Regex 解析每行日誌"]

    Start --> ProcessTimer["每 30 秒 ProcessTimer"]
    --> CheckProcess["檢查 EFT 行程<br/>EscapeFromTarkov.exe"]
    --> FireGameStarted["GameStarted 事件"]

    Start --> ScreenshotWatch["監控 Screenshots/\nFileSystemWatcher"]
    --> NewPng["新 .png 檔案"]
    --> ParseFilename["Regex 解析檔案名稱<br/>擷取座標 + 四元數"]
    --> FirePlayerPos["PlayerPosition 事件"]
```

---

## 日誌檔案的選取邏輯

### 目錄結構

```
{EFT安裝目錄}/Logs/
├── log_2024.01.15_10-30-45/      # 每場遊戲連線建立一個資料夾
│   ├── application.log            # 主遊戲日誌（地圖載入、配對、遊戲狀態）
│   ├── application_000.log        # 輪替備份（檔案過大時自動產生）
│   ├── notifications.log          # 遊戲內通知（組隊、聊天、跳蚤市場、任務）
│   ├── notifications_000.log
│   ├── traces.log                 # 追蹤日誌（目前未使用，直接跳過）
│   └── traces_000.log
└── log_2024.01.15_12-15-20/
    └── ...
```

### 判斷流程

```mermaid
flowchart TD
    FindLogsPath["從 Windows Registry 取得 Logs/ 路徑<br/>SOFTWARE\\Wow6432Node\\...\\EscapeFromTarkov<br/>或 Steam App 3932890"]
    --> FindLatest["掃描 Logs/ 下所有 log_yyyy.MM.dd_H-mm-ss/ 資料夾<br/>取時間最新者"]
    --> WatchFolder["FileSystemWatcher 監控 Logs/<br/>偵測新資料夾與新檔案建立"]

    WatchFolder --> NewAppLog{"新檔案名稱包含<br/>application.log 或<br/>application_000.log?"}
    NewAppLog -->|是| StartAppMonitor["為此檔案建立 LogMonitor<br/>GameLogType.Application"]
    NewAppLog -->|否| SkipApp["跳過"]

    WatchFolder --> NewNotifLog{"新檔案名稱包含<br/>notifications.log 或<br/>notifications_000.log?"}
    NewNotifLog -->|是| StartNotifMonitor["為此檔案建立 LogMonitor<br/>GameLogType.Notifications"]
    NewNotifLog -->|否| SkipNotif["跳過"]

    WatchFolder --> NewTraces{"新檔案名稱包含<br/>traces.log 或<br/>traces_000.log?"}
    NewTraces -->|是| SkipTraces["忽略／跳過<br/>（不建立監控）"]
    NewTraces -->|否| SkipOther["忽略<br/>（不是已知類型）"]

    StartAppMonitor --> AppInit["LogMonitor.Start()<br/>GameLogType.Application"]
    StartNotifMonitor --> NotifInit["LogMonitor.Start()<br/>GameLogType.Notifications"]

    NotifInit --> SkipExisting["fileBytesRead = 檔案當前大小<br/>跳過既有內容，只讀新資料"]
    --> FireInitComplete["立即觸發 InitialReadComplete"]

    AppInit --> ReadFromStart["fileBytesRead = 0<br/>從頭開始讀取"]
    --> FireInitRead["第一次增量讀取時<br/>InitialRead = true"]
    --> FireAppInitComplete["觸發 InitialReadComplete<br/>之後 InitialRead = false"]
```

### 三種日誌類型的差異

| 類型 | 檔案名稱 | 初始讀取策略 | 事件來源 |
|------|----------|-------------|----------|
| `Application` | `application.log` / `application_000.log` | 從頭讀取（`fileBytesRead=0`） | Profile、地圖、戰局、配對、控制設定 |
| `Notifications` | `notifications.log` / `notifications_000.log` | 跳過既有內容（`fileBytesRead=檔案大小`） | 組隊、聊天、跳蚤市場、任務 |
| `Traces` | `traces.log` / `traces_000.log` | **不監控**（直接 `continue`） | 無 |

### 初始讀取（InitialRead）的影響

Application 日誌的第一次增量資料會被標記為 `InitialRead=true`，此時 **只處理**：
- `Session mode:` → 設定 Profile type
- `SelectProfile/SelectedProfile ProfileId:` → 設定 Profile ID
- `Control settings:` → 觸發 ControlSettings 事件

其餘所有事件（組隊、地圖、戰局、聊天等）在 `InitialRead=true` 時全部跳過，避免重複觸發歷史事件。

### 歷史日誌回讀（ProcessLogs）

`ProcessLogs()` 用於從斷點回讀歷史日誌：
1. 從 `GetLogFolders()` 取得所有 `log_*/` 資料夾（按時間排序）
2. 在每個資料夾中掃描 `application.log` / `notifications.log`（跳過 `traces.log` 與未知檔案）
3. 逐行 Regex 匹配，依時間範圍過濾（`>= breakpoint.Date` 且 `< nextProfile.Date`）
4. 對每條匹配行呼叫 `GameWatcher_NewLogData()`，與即時監控共用相同的事件判定邏輯

---

## 日誌行解析流程

```mermaid
flowchart TD
    RawData["LogMonitor 傳入原始字串<br/>(NewLogDataEventArgs)"]
    --> RegexSplit["Regex 多行匹配<br/>logPattern<br/>(?&lt;date&gt;...)(?&lt;time&gt;...)\\|(?&lt;message&gt;...)(?&lt;json&gt;...)"]
    --> ForEachLine["逐行處理"]

    ForEachLine --> IsInit{"e.InitialRead?"}
    
    IsInit -->|"是（首次讀取）"| InitProcess["處理部分事件<br/>Session mode<br/>SelectProfile<br/>Control settings"]
    IsInit -->|"否（增量讀取）"| FullProcess["處理所有事件"]

    InitProcess --> ParseSessionModeInit
    InitProcess --> ParseSelectProfileInit
    InitProcess --> ParseControlSettings
    InitProcess --> SkipOthers["跳過後續所有事件"]
    SkipOthers --> NextLineInit["處理下一行"]

    FullProcess --> ParseSessionModeFull
    FullProcess --> ParseSelectProfileFull
    FullProcess --> ParseControlSettings
    FullProcess --> ParseGroupEvents
    FullProcess --> ParseMapRaidEvents
    FullProcess --> ParseChatEvents
    FullProcess --> NextLineFull["處理下一行"]
```

---

## 事件判定決策樹

### 1. Profile 切換事件（Initial Read 也處理）

```mermaid
flowchart LR
    Input1["日誌行包含:<br/>'Session mode: '"]
    --> MatchMode["Regex 提取 mode<br/>Pve / Regular"]
    --> SetProfileType["設定 CurrentProfile.Type"]

    Input2["日誌行包含:<br/>'SelectProfile ProfileId:'<br/>或 'SelectedProfile ProfileId:'"]
    --> MatchProfile["Regex 提取 profileId<br/>+ accountId"]
    --> SetProfile["設定 CurrentProfile.Id<br/>+ CurrentProfile.AccountId"]
    --> IsInitCheck{"e.InitialRead?"}
    IsInitCheck -->|是| InitDone["僅設定，不觸發事件"]
    IsInitCheck -->|否| HasRaidStarted{"raidInfo.StartedTime != null<br/>&& raidInfo.EndedTime == null"}
    HasRaidStarted -->|是| FireRaidEnded["RaidEnded 事件"]
    HasRaidStarted -->|否| FireProfileChanged["ProfileChanged 事件"]

    Input3["日誌行包含:<br/>'Control settings:'"]
    --> HasJson{"JSON 群組匹配成功?"}
    HasJson -->|是| FireControlSettings["ControlSettings 事件<br/>傳入 JSON 節點"]
    HasJson -->|否| Skip["跳過"]
```

### 2. 組隊事件（僅增量讀取）

```mermaid
flowchart LR
    InputGroup["日誌行包含:<br/>'Got notification | GroupMatch...'"]
    --> CheckInviteAccept{"GroupMatchInviteAccept"}
    CheckInviteAccept -->|是| FireGroupInviteAccept["GroupInviteAccept 事件<br/>JSON → GroupLogContent"]

    InputGroup --> CheckUserLeave{"GroupMatchUserLeave"}
    CheckUserLeave -->|是| FireGroupUserLeave["GroupUserLeave 事件<br/>JSON → GroupMatchUserLeaveLogContent"]

    InputGroup --> CheckDisband{"GroupMatchWasRemoved"}
    CheckDisband -->|是| FireGroupDisbanded["GroupDisbanded 事件"]

    InputGroup --> CheckRaidSettings{"GroupMatchRaidSettings"}
    CheckRaidSettings -->|是| FireGroupRaidSettings["GroupRaidSettings 事件<br/>JSON → GroupRaidSettingsLogContent"]

    InputGroup --> CheckRaidReady{"GroupMatchRaidReady"}
    CheckRaidReady -->|是| FireGroupMemberReady["GroupMemberReady 事件<br/>JSON → GroupMatchRaidReadyLogContent"]
```

### 3. 地圖與戰局事件（僅增量讀取，核心流程）

```mermaid
flowchart TD
    InputMap["日誌行包含特定字串"]
    
    InputMap --> CheckMapLoading{"scene preset path:maps"}
    CheckMapLoading -->|是| NewRaidInfo["建立全新 raidInfo 物件"]
    --> ExtractBundle["Regex 提取 bundle 名稱<br/>e.g. customs_preset"]
    --> LookupMap["查詢 MapBundles 字典<br/>customs_preset → bigmap"]
    --> FireMapLoading["MapLoading 事件"]

    InputMap --> CheckLocationLoaded{"LocationLoaded"}
    CheckLocationLoaded -->|是| ExtractLoadTime["Regex 提取 loadTime"]
    --> SetMapLoadTime["設定 raidInfo.MapLoadTime"]

    InputMap --> CheckMatchingCompleted{"MatchingCompleted"}
    CheckMatchingCompleted -->|是| ExtractQueueTime["Regex 提取 queueTime"]
    --> SetQueueTime["設定 raidInfo.QueueTime"]

    InputMap --> CheckProfileStatus{"TRACE-NetworkGameCreate<br/>profileStatus"}
    CheckProfileStatus -->|是| ExtractRaidInfo["Regex 提取 Location,<br/>RaidMode, shortId"]
    --> SetRaidInfo["設定 raidInfo.Map<br/>raidInfo.Online<br/>raidInfo.RaidId"]
    --> CheckReconnect{"Raids 字典<br/>已有此 RaidId?"}
    CheckReconnect -->|是| SetReconnected["raidInfo.Reconnected = true<br/>還原舊 raidInfo"]
    CheckReconnect -->|否| AddToRaids["加入 Raids 字典"]
    --> CheckMatchFound{"!Reconnected<br/>&& Online<br/>&& QueueTime > 0"}
    CheckMatchFound -->|是| FireMatchFound["MatchFound 事件"]
    CheckMatchFound -->|否| SkipMatchFound["跳過"]
    --> CheckMapUnknown{"之前地圖未知?"}
    CheckMapUnknown -->|是| RetroMapLoading["MapLoading 事件"]
    CheckMapUnknown -->|否| SkipRetroMap["跳過"]
    --> FireMapLoaded["MapLoaded 事件<br/>（一定觸發）"]

    InputMap --> CheckGameStarting{"GameStarting"}
    CheckGameStarting -->|是| CheckReconGS{"!Reconnected"}
    CheckReconGS -->|是| SetStartingTime["設定 raidInfo.StartingTime"]
    FireRaidStarting["RaidStarting 事件"]

    InputMap --> CheckGameStarted{"GameStarted"}
    CheckGameStarted -->|是| CheckReconGSt{"!Reconnected"}
    CheckReconGSt -->|是| SetStartedTime["設定 raidInfo.StartedTime"]
    FireRaidStarted["RaidStarted 事件"]

    InputMap --> CheckMatchingAbort{"Matching aborted<br/>或 Matching cancelled"}
    CheckMatchingAbort -->|是| FireMatchingAborted["MatchingAborted 事件"]
    --> ResetRaidInfo["重置 raidInfo<br/>（保留 Profile）"]

    InputMap --> CheckUserMatchOver{"UserMatchOver"}
    CheckUserMatchOver -->|是| ParseUserMatchOver["解析 JSON<br/>提取 location + shortId"]
    --> FireRaidExited["RaidExited 事件"]
    --> ResetRaidInfo2["重置 raidInfo<br/>（保留 Profile）"]

    InputMap --> CheckInitVersion{"Init: pstrGameVersion:"}
    CheckInitVersion -->|是| CheckRaidEnded{"raidInfo.EndedTime != null"}
    CheckRaidEnded -->|是| FireExitedPostRaid["ExitedPostRaidMenus 事件"]
    --> ResetRaidInfo3["重置 raidInfo<br/>（保留 Profile）"]
```

### 4. 聊天與跳蚤市場事件

```mermaid
flowchart TD
    ChatInput["日誌行包含:<br/>'Got notification | ChatMessageReceived'"]
    --> DeserializeChat["JSON → ChatMessageLogContent"]
    --> CheckType{"message.type"}
    CheckType -->|PlayerMessage = 1| SkipChat["跳過（忽略）"]
    CheckType -->|FleaMarket = 4| ParseFlea["JSON → SystemChatMessageLogContent"]
    --> CheckTemplate{"templateId"}
    CheckTemplate -->|"5bdabfb886f7743e152e867e 0"| FireFleaSold["FleaSold 事件<br/>JSON → FleaSoldMessageLogContent"]
    CheckTemplate -->|"5bdabfe486f7743e1665df6e 0"| FireFleaExpired["FleaOfferExpired 事件<br/>JSON → FleaExpiredMessageLogContent"]
    CheckType -->|"TaskStarted(10)<br/>~ TaskFinished(12)"| ParseTask["JSON → TaskStatusMessageLogContent"]
    --> FireTaskModified["TaskModified 事件"]
    --> CheckTaskStatus{"Status"}
    CheckTaskStatus -->|Started| FireTaskStarted["TaskStarted 事件"]
    CheckTaskStatus -->|Failed| FireTaskFailed["TaskFailed 事件"]
    CheckTaskStatus -->|Finished| FireTaskFinished["TaskFinished 事件"]
```

---

## 完整事件列表

| 事件 | 觸發時機 | 資料來源 |
|------|----------|----------|
| `GameStarted` | EFT 程序首次被偵測到 | ProcessTimer (30s) |
| `ProfileChanged` | 切換 Profile（非初始讀取） | application.log |
| `ControlSettings` | 讀取控制設定 | application.log |
| `GroupInviteAccept` | 組隊邀請被接受 | notifications.log |
| `GroupUserLeave` | 隊員離開隊伍 | notifications.log |
| `GroupDisbanded` | 隊伍解散 | notifications.log |
| `GroupRaidSettings` | 隊長設定戰局參數 | notifications.log |
| `GroupMemberReady` | 隊員準備就緒 | notifications.log |
| `MapLoading` | 地圖開始載入 / 偵測到地圖 | application.log |
| `MatchFound` | 配對完成（僅首次，非重連） | application.log |
| `MapLoaded` | 地圖載入 + 連線建立（一定觸發） | application.log |
| `MatchingAborted` | 取消配對 | application.log |
| `RaidStarting` | PMC 倒數開始（或 Scav 直接開始） | application.log |
| `RaidStarted` | 正式進入戰局 | application.log |
| `RaidExited` | 戰局結束撤離 | notifications.log |
| `RaidEnded` | 切換 Profile 時結束前一個戰局 | application.log |
| `ExitedPostRaidMenus` | 返回主選單 | application.log |
| `FleaSold` | 跳蚤市場物品售出 | notifications.log |
| `FleaOfferExpired` | 跳蚤市場報價過期 | notifications.log |
| `TaskModified` | 任務狀態變更 | notifications.log |
| `TaskStarted` | 任務開始（= TaskModified 的子集） | notifications.log |
| `TaskFailed` | 任務失敗（= TaskModified 的子集） | notifications.log |
| `TaskFinished` | 任務完成（= TaskModified 的子集） | notifications.log |
| `PlayerPosition` | 遊戲內截圖時 | Screenshots/*.png 檔案 |
| `InitialReadComplete` | 所有 LogMonitor 初次讀取完成 | LogMonitor |

---

## RaidInfo 狀態機

```mermaid
flowchart TD
    Start(["new RaidInfo()"]) --> Empty["Empty<br/>Profile 保留不重置"]
    Empty -->|"scene preset path:maps"| MapLoading["MapLoading"]
    MapLoading -->|"LocationLoaded"| Matching["Matching"]
    Matching -->|"MatchingCompleted"| Queued["Queued"]
    Queued -->|"TRACE-NetworkGameCreate"| Connected["Connected"]

    Connected -->|"GameStarting"| Starting["Starting"]
    Starting -->|"GameStarted"| Started["Started"]
    Started -->|"UserMatchOver"| Exited["Exited"]
    Exited -->|"Init pstrGameVersion"| Start

    Connected -->|"Matching aborted/cancelled"| Aborted["Aborted"]
    Aborted -->|"raidInfo 重置"| Start

    subgraph Connected["Connected 內部"]
        CEntry(["進入"]) --> CCheckReconnect{"Raids 字典已有此 RaidId?"}
        CCheckReconnect -->|"否，首次 + QueueTime > 0"| CMatchFound["MatchFound 事件"]
        CCheckReconnect -->|"是/否"| CMapLoaded["MapLoaded 事件（一定觸發）"]
    end
```

---

## 註解

- **InitialRead 邏輯**：非 `Application` 類型的日誌（`notifications.log`）在 LogMonitor 啟動時直接跳到檔案末尾，跳過既有內容。`Application` 類型的日誌在首次增量讀取完成後觸發 `InitialReadComplete`，在此之前的資料只處理 Profile/ControlSettings 事件，不觸發其他事件。
- **raidInfo 生命週期**：`raidInfo` 在 `MapLoading` 時新建，在 `MatchingAborted` / `UserMatchOver` / `ExitedPostRaidMenus` 時重置（保留 `Profile` 欄位）。
- **地圖名稱解析**：透過 `MapBundles` 字典將 Bundle 名稱（如 `customs_preset`）映射到已知地圖 ID（如 `bigmap`）。
