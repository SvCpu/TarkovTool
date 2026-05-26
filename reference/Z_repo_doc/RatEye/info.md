# RatEye

開源的逃離塔科夫圖像處理函式庫（.NET）。

提供圖像分析能力，可作為其他工具（如 RatScanner）的底層視覺識別引擎，
用於截圖分析與物品識別。

## 視覺識別原理

### 模板圖標來源

**倉庫本身不存放任何遊戲物品圖標。** 識別用的模板圖標全部在執行時期從外部載入：
- **靜態圖標**：使用者提供的 `Data/name/{itemId}.png`
- **動態圖標**：來自 `%Temp%/Battlestate Games/EscapeFromTarkov/Icon Cache/`（遊戲快取目錄）

倉庫內嵌的 PNG（約 23 個）均為輔助性 UI 元素：放大鏡搜尋標記、網格邊框紋理、武器配件槽位背景圖示，用於介面定位與圖標合成。

### 圖標到物品名稱的映射

#### 靜態圖標

**不使用 index.json。** 檔案名稱本身就是物品的 BSG UID：

```
{5a608bf24f39f98ffc77720e}.png  →  移除副檔名得 5a608bf24f39f98ffc77720e
                                  →  RatStashDB.GetItem("5a608bf24f39f98ffc77720e")
                                  →  取得對應的 Item 物件（含名稱、類別等）
```

對應實作：`IconManager.LoadStaticCorrelationData()` 掃描所有 `*.png`，用 `Path.GetFileNameWithoutExtension()` 取出 ID 後查 RatStash。

#### 動態圖標（遊戲快取）

遊戲快取目錄中有以數字命名的 `.png` 和一個 `index.json`（理論上將數字 → BSG UID → 物品名稱）。然而在此版本程式碼中，`Path.cs:58` 雖定義了 `DynamicCorrelationData = index.json` 路徑，但該檔案**從未被實際解析載入**，`_dynamicCorrelationData` 始終為空字典，動態圖標的模板匹配實際上是空的。

| 圖標類型 | 映射方式 | index.json 是否使用 |
|---|---|---|
| 靜態圖標 | 檔名 = 物品ID → RatStash | 不使用 |
| 動態圖標 | 路徑已定義，載入邏輯未實作 | 未使用 |

### 三種識別模式

#### 1. 背包網格識別（Inventory）

對截圖做 HSV 顏色過濾提取網格線 → 形態學操作平滑 → 掃描網格定位每個圖標的裁剪區域。

#### 2. 圖標物品識別（Icon）

- **模板匹配（預設）**：將裁剪出的圖標縮放到與模板一致的比例，對每個已載入的外部模板逐一呼叫 OpenCV 的 `MatchTemplate` + `TM_SQDIFF_NORMED`，取置信度最高者。支援 90° 旋轉匹配。
- **OCR 模式**：提取圖標上方標題區域 → Tesseract LSTM 辨識文字 → Levenshtein 距離模糊匹配物品名稱。

比對結果透過 `IconManager` 查詢 `RatStash` 物品資料庫取得完整物品資訊。

#### 3. 檢視窗口識別（Inspection / MultiInspection）

用內嵌的放大鏡圖示進行模板匹配定位檢視窗 → 偵測關閉按鈕確定標題區域 → Tesseract OCR 讀取物品名稱 → Levenshtein 模糊匹配。

### 完整流程

```
螢幕截圖 → 網格檢測 → 裁剪圖標區域 → MatchTemplate 逐一比對外部模板
                                             ↓
                 取最高置信度 → IconManager 查 RatStash → 回傳物品物件
```
