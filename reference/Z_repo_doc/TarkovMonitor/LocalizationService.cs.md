# LocalizationService.cs

多國語系服務，支援執行時即時切換 UI 語言。

## 機制

使用兩層回退的字串查詢：

```
GetString(key)
  └─ IStringLocalizer[key]  (ASP.NET Core 泛用本地化)
       ├─ 找到 → 回傳值
       └─ ResourceNotFound → Properties.Resources.ResourceManager.GetString(key, CurrentUICulture)
            ├─ 找到 → 回傳值
            └─ 未找到 → 回傳 key 本身（fallback）
```

## 支援語言

| 代碼 | 語言 |
|---|---|
| `de` | German |
| `en` | English |
| `es` | Spanish |
| `fr` | French |
| `pl` | Polish |
| `pt` | Portuguese |
| `ru` | Russian |
| `zh` | Chinese |

## 切換語言

`SetCulture(cultureName)`：
1. 建立 `CultureInfo` 物件
2. 設定 `CultureInfo.CurrentCulture`（數字/日期格式）與 `CurrentUICulture`（字串資源）
3. 將選擇存入 `Properties.Settings.Default.language` 並持久化
4. 觸發 `LanguageChanged` 事件，通知 UI 重新載入字串

若傳入不存在的文化代碼，捕獲 `CultureNotFoundException` 並回退到英文。

## 初始化

構造函數從 `Properties.Settings.Default.language` 讀取上次選擇的語言，啟動時自動套用。

## 與 WinForms 整合

`IStringLocalizerFactory` 透過 DI 注入，基底字串資源位於 `Properties.Strings`（`Strings.resx`），但最終顯示的字串經由 `IStringLocalizer` 的命名空間解析機制取得，不直接操作 `.resx` 檔案。

## 相關檔案

- `Properties/Strings.resx`：預設英文資源
- `Properties/Strings.{culture}.resx`：各語言資源檔（如 `Strings.zh.resx`）
- `Settings.Default.language`：使用者偏好設定（持久化在 `user.config`）
