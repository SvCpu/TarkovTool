# TILDA-EFT 螢幕物品偵測分析

## 概述

TILDA-EFT 是一款 Python 撰寫的《逃離塔科夫》物品掃描器，透過**螢幕截圖 + 電腦視覺**技術辨識遊戲中的物品，不涉及遊戲記憶體讀取。核心程式碼位於 `Tilda Source/main.py`。

---

## 兩種掃描模式

### 1. 被動掃描 (Passive / Secondary Scan)

**觸發方式**: 預設快捷鍵 `Ctrl+Shift+S`

**流程** (`main.py:415-456`, `text_grab("P")` 分支):

```
1. pyautogui.position()         → 取得滑鼠當前座標 (posx, posy)
2. pyautogui.screenshot(region=(posx, posy-70, 500, 70))
                                → 在滑鼠上方 70px 處截取 500x70 區域 (tooltip 出現前)
3. cv2.cvtColor(→GRAY) + cv2.bitwise_not
                                → 轉灰階並反色
4. time.sleep(1.3)              → 等待遊戲 tooltip 浮出
5. 同樣區域再截一次圖            → 此時 tooltip 已出現
6. cv2.subtract(第二張, 第一張)  → 兩圖相減，得到 tooltip 區域的差異
7. numpy 篩選: 像素值 > [2,2,2] 設為白色 [255,255,255]
                                → 過濾雜訊，保留 tooltip 文字變化區域
8. numpy.where(na==[255,255,255]) → 找出白色像素的座標
9. 取 hoverY[0]~hoverY[-1], hoverX[0]~hoverX[-1]
                                → 計算 tooltip 的邊界框 (bounding box)
10. ROI = numpyarray_orig[top:bottom, left:right]
                                → 從原始截圖裁切出 tooltip 區域
11. pytesseract.image_to_string(ROI)
                                → OCR 辨識物品名稱
```

**核心技術**: 影像減法 (image subtraction) — 利用 tooltip 浮出前後的截圖差異來定位物品名稱區域。

---

### 2. 主動掃描 (Active / Primary Scan)

**觸發方式**: 預設快捷鍵 `~` (波浪號)

**流程** (`main.py:457-513`, `text_grab("A")` 分支):

```
1. pyautogui.screenshot()       → 全螢幕截圖
2. cv2.imread("search_icon_image.png")
                                → 載入搜尋圖示範本 (放大鏡圖示)
3. cv2.matchTemplate(template, scrot, cv2.TM_SQDIFF_NORMED)
                                → 在截圖中搜尋放大鏡圖示
4. cv2.minMaxLoc(result)        → 找到最佳匹配位置 (MPx, MPy)
5. pyautogui.screenshot(region=(MPx, MPy, 642, 25))
                                → 在放大鏡右方截取物品名稱標題列
6. pytesseract.image_to_string(header)
                                → OCR 辨識物品名稱
```

**若標準匹配失敗 (多尺度降級方案)** (`main.py:488-511`):

```
1. cv2.cvtColor(scrot, cv2.COLOR_BGR2GRAY) → 灰階化
2. for scale in numpy.linspace(0.0, 2.0, 20)[::-1]:
     imutils.resize(template, width=int(template.shape[1] * scale))
     cv2.matchTemplate(scrot, resized, cv2.TM_CCOEFF_NORMED)
                                → 多尺度縮放範本重新匹配
3. 找到匹配後在該位置截取物品名稱區域進行 OCR
```

**核心技術**: 範本匹配 (template matching) — 用放大鏡圖示定位物品訊息視窗，再 OCR 讀取物品名稱。

---

## 物品名稱模糊匹配 (`main.py:520-527`)

OCR 結果並非直接用於查詢，而是透過 `difflib.get_close_matches()` 與資料庫中的物品名稱清單進行**模糊匹配**，以補償 OCR 的辨識誤差。

```python
text = text_grab(type)                          # OCR 結果
item_list = dbman.item_list                     # 從 SQLite 載入物品名稱清單
close_matches = difflib.get_close_matches(text, item_list)
closest = close_matches[0]                      # 取最接近的匹配
```

---

## 物品資料查詢 (`main.py:529-673`)

使用 SQLite 資料庫 (`item_info.sql`)，由 `dbman.py` 從 [Tarkov API](https://api.tarkov.dev/graphql) 取得資料並建表:

- **items**: id, name, shortName, avg24hPrice, wikiLink, iconLink, width, height, lastLowPrice
- **sellFor**: 各商人收購價格
- **buyFor**: 各商人販售價格
- **usedInTasks**: 用於哪些任務

查詢結果顯示:
- 物品名稱
- 24小時平均 flea market 價格
- 最佳販售商人及價格
- 每格價值 (price per slot)
- 用於多少任務
- 物品圖示 (從網路下載)
- Wiki 連結

---

## 使用到的函式庫

| 函式庫 | 用途 |
|--------|------|
| `pyautogui` | 滑鼠位置取得、螢幕截圖、滑鼠點擊 |
| `opencv-python (cv2)` | 影像處理: 灰階化、反色、影像減法、範本匹配 |
| `numpy` | 像素陣列操作、條件過濾、座標定位 |
| `pytesseract` | OCR 文字辨識 (需 Tesseract-OCR 引擎) |
| `PIL (Pillow)` | 圖片格式轉換 (numpy array ↔ Image) |
| `difflib` | 物品名稱模糊比對 |
| `pynput` | 全域快捷鍵監聽 (GlobalHotKeys) |
| `PySide6` | GUI 介面 (主視窗 + 覆層) |
| `imutils` | 多尺度範本匹配時的圖片縮放 |
| `sqlite3` | 本地物品資料庫 |
| `requests` | 從 API 拉取物品資料、下載物品圖示 |

---

## 系統架構圖

```
┌─────────────────────────────────────────────────────┐
│                   main.py                            │
│                                                      │
│  key_event_ear() ← pynput.GlobalHotKeys             │
│       │                                              │
│       ├─ item_scan_quick() → item_lookup("P")       │
│       │      └─ text_grab("P")  (被動掃描)           │
│       │           ├─ pyautogui.screenshot ×2        │
│       │           ├─ cv2.subtract(前,後)             │
│       │           ├─ numpy.where → bounding box     │
│       │           └─ pytesseract → OCR              │
│       │                                              │
│       └─ item_scan_full() → item_lookup("A")        │
│              └─ text_grab("A")  (主動掃描)           │
│                   ├─ pyautogui.screenshot           │
│                   ├─ cv2.matchTemplate(放大鏡圖示)   │
│                   └─ pytesseract → OCR              │
│                                                      │
│  item_guess(type)                                    │
│       └─ difflib.get_close_matches(OCR_text, db)    │
│            └─ item_lookup(type)                     │
│                 ├─ sqlite3 查詢物品資訊              │
│                 ├─ requests.get(iconLink) 下載圖示   │
│                 └─ 更新 UI 顯示結果                  │
│                                                      │
├─────────────────────────────────────────────────────┤
│  dbman.py                                            │
│  refresh_database()                                  │
│       ├─ requests.post(api.tarkov.dev/graphql)       │
│       └─ sqlite3 寫入 items / sellFor / buyFor /    │
│          usedInTasks 四張表                          │
└─────────────────────────────────────────────────────┘
```

---

## 關鍵參數

| 參數 | 值 | 位置 |
|------|-----|------|
| 被動掃描截圖範圍 | (posx, posy-70, 500, 70) | `main.py:424` |
| 被動掃描延遲 | 1.3 秒 | `main.py:426` |
| 像素差異閾值 | > [2, 2, 2] | `main.py:441` |
| 主動掃描標題列寬度 | 642 px | `main.py:480` |
| 主動掃描標題列高度 | 25 px | `main.py:480` |
| 多尺度範本範圍 | 0.0 ~ 2.0, 20 階 | `main.py:493` |
| TM_SQDIFF_NORMED 匹配 | 主動掃描標準 | `main.py:473` |
| TM_CCOEFF_NORMED 匹配 | 多尺度降級方案, threshold=0.8 | `main.py:496-498` |
| Tesseract OCR 路徑 | 設定於 settings.ini | `prefs_writer.py:104` |
