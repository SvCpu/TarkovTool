# UpdateCheck.cs

GitHub 版本更新檢查模組，使用 **Refit**（宣告式 REST 客戶端函式庫）呼叫 GitHub Releases API。

## 流程

1. **靜態初始化**：設定間隔 **24 小時**的定時器（`updateCheckTimer`），啟用時自動觸發版本檢查。
2. **檢查方法** `CheckForNewVersion()`：
   - 請求 `https://api.github.com/repos/the-hideout/TarkovMonitor/releases/latest`
   - 從回應 JSON 的 `tag_name` 解析為 `Version` 物件
   - 從當前組件中讀取 `Assembly.GetExecutingAssembly().GetName().Version` 作為本機版本
   - 若 **local < remote**（`CompareTo` 回傳 -1），觸發 `NewVersion` 事件（附帶 `Version` 與 GitHub Release 連結 `html_url`）
3. **錯誤處理**：API 回應異常 (`ApiException`) 或其它錯誤均觸發 `Error` 事件。

## 介面定義

```csharp
public interface IGitHubAPI
{
    [Get("/releases/latest")]
    [Headers("user-agent: tarkov-monitor")]
    Task<ReleaseData> GetLatestRelease();
}
```

## 資料模型

```csharp
public class ReleaseData
{
    public string tag_name { get; set; }  // 版本號字串，如 "1.3.0.0"
    public string html_url { get; set; }  // Release 頁面連結
}
```

## 發佈流程

註解提示標籤格式：`git tag 1.0.1.2` → `git push origin 1.0.1.2`。

