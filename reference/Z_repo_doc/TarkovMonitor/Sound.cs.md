# Sound.cs

音效播放模組，使用 **NAudio** 函式庫播放 MP3 音效。

## 音效來源

支援兩層機制，優先回退：

1. **自訂音效**：使用者自行複製到 `{AppData}/sounds/{key}.mp3` 的檔案
2. **內嵌資源**：編譯在 `Properties.Resources` 中的預設音效（二進位資料）

`Play(key)` 先檢查 `IsCustom(key)`，若存在自訂檔則讀取檔案位元組，否則從資源管理器取得。

## 音效類型 (`SoundType`)

| enum 值 | 用途 |
|---|---|
| `air_filter_off` | 空濾關閉 |
| `air_filter_on` | 空濾開啟 |
| `match_found` | 配對成功 |
| `raid_starting` | 倒數開始 |
| `restart_failed_tasks` | 重新啟動失敗任務 |
| `runthrough_over` | 撤離結束 |
| `scav_available` | Scav 準備就緒 |
| `quest_items` | 任務物品 |

## 播放裝置

- `GetPlaybackDevices()` 列舉系統所有 `WaveOut` 輸出裝置
- 可透過設定 `notificationsDevice`（裝置編號）指定播放裝置，`-1` 代表系統預設

## 播放流程

```
Play(key)
  └─ IsCustom(key) → File.Exists(CustomSoundsPath/{key}.mp3)
       ├─ True  → File.ReadAllBytes
       └─ False → Properties.Resources.ResourceManager.GetObject(key) as byte[]
  └─ Mp3FileReader(stream) 解碼 MP3
  └─ WaveOut.Init(reader)  初始化播放
  └─ WaveOut.Play()        開始播放
  └─ 每 100ms 輪詢 PlaybackState 直到停止
```

## 儲存路徑

`AppDataFolder` 來自 `Application.UserAppDataPath`（.NET WinForms 屬性），通常為：
```
C:\Users\{使用者}\AppData\Local\TarkovMonitor\TarkovMonitor\1.0.0.0\
```
自訂音效存放於其下的 `sounds\` 子目錄。

## API 摘要

| 方法 | 功能 |
|---|---|
| `SoundPath(key)` | 回傳 `{AppData}/sounds/{key}.mp3` 路徑 |
| `SetCustomSound(key, path)` | 複製外部 MP3 到自訂音效目錄 |
| `RemoveCustomSound(key)` | 刪除自訂音效檔案 |
| `IsCustom(key)` | 檢查是否有自訂音效（快取） |
| `Play(key)` | 非同步播放指定音效 |
| `GetPlaybackDevices()` | 列舉音效輸出裝置 |
