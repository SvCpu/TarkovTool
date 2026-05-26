# Tarkov Market Helper（已棄用）

[GitHub](https://github.com/null-architect/tarkov_market_helper)

遊戲內市場價格輔助工具，在滑鼠指向物品時顯示最低價、每格價格、商人收購價。

**注意：此專案已凍結不再維護。**

---

## 物品識別原理

### 方法：感知雜湊（Perceptual Hashing）

不同於 RatEye（模板匹配）或 eft-where-am-i（座標讀取），此工具使用**MD5 像素指紋**來辨識物品：

```
滑鼠移至物品上方
  → 截取全螢幕（僅支援 1920×1080 無邊框模式）
  → 轉灰階
  → 從滑鼠位置往左上偏移 (11, -11) 找到起始像素
  → 向右掃描，尋找值為 87 的邊界（右角）
  → 向上掃描，尋找值為 87 的邊界（上角）
  → 裁切出物品圖標區域
  → 二值化（threshold）
  → 對像素位元組計算 MD5 值
  → 以 MD5 作為 Key 查詢價格資料庫
```

**值為 87 的邊界**是 EFT 物品欄中圍繞物品圖標的灰色邊框在灰階下的像素值。

### 識別流程

```
scan.py:Scan.__init__()
  → 截圖、灰階化
  → find_start_shade()      滑鼠偏移定位
  → find_right_corner()     掃描水平灰色邊框
  → find_top_corner()       掃描垂直灰色邊框
  → find_item_image()       裁切 + 二值化
  → hash_item_image()       計算 MD5

main_frame.py:MainFrame.update_frame()
  → scan_item()
    → Scan().item_hash
    → Items.find(hash)
      → 在 DataFrame 中比對 Hash 欄位
      → 回傳價格資料

items.py:Items.__init__()
  → update_data()
    → GET Google Spreadsheet CSV（啟動時載入一次）
    → pandas read_csv 解析
```

### 與 RatEye 的差異

| 特性 | RatEye | Tarkov Market Helper |
|---|---|---|
| 辨識方式 | OpenCV MatchTemplate（模板匹配） | MD5 像素指紋 + 資料庫查詢 |
| 模板來源 | 外部 `Data/name/*.png` | Google Spreadsheet CSV（預先計算的 Hash → 價格） |
| 旋轉處理 | 支援 ±90° | 不支援 |
| 語系支援 | Tesseract OCR | EN / RU 兩種雜湊值 |
| 螢幕解析度 | 不限 | 僅 1920×1080 |

## 遊戲物品圖像來源

**此倉庫不包含任何遊戲物品圖像。**

- 工具本身**僅顯示價格文字**（₽ m/s/t），不顯示物品圖標
- 辨識用的「參考資料」存於 **Google Spreadsheet**：
  ```
  https://docs.google.com/spreadsheet/ccc?key=12iocznEgCgCTOjPxEkRHxLV18fzHV2WqtdJQZFwTjtY&output=csv
  ```
- 該 CSV 包含：
  - `Hash EN` / `Hash RU`：預先從遊戲截圖中計算好的 MD5 值
  - `Lowest price`、`Price per slot`、`Trader price`：對應的市場價格
- 這些雜湊值是在工具開發階段從**實際遊戲截圖**中逐一收集計算的，類似於建立一個指紋資料庫

## 限制

- 僅支援無邊框模式、1920×1080 解析度
- 僅支援 EN / RU 遊戲客戶端
- 物品名稱觸及螢幕右緣時無法辨識
- 商人交易介面中無法顯示價格
