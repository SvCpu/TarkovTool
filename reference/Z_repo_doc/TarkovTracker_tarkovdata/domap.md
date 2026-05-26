# 利用 maps.json + SVG 實現座標定位功能

## 原理概述

maps.json 為每張地圖定義了遊戲座標到 SVG 像素的映射範圍（`bounds`），
SVG 地圖本身已按樓層分組（`<g id="Ground_Level">`），
因此可將遊戲座標（如從截圖檔名解析出的 x, z）轉換為 SVG 上的像素位置並疊加標記。

---

## 步驟

### 1. 選取地圖

從 maps.json 取出目標地圖的資料：

```json
{
  "factory": {
    "svg": {
      "file": "Factory.svg",
      "floors": ["Basement", "Ground_Floor", "First_Floor", "Second_Floor"],
      "defaultFloor": "Ground_Floor",
      "coordinateRotation": 90,
      "bounds": [[-67, 69], [76.6, -65.5]]
    }
  }
}
```

### 2. 載入 SVG 並取得 viewBox

解析 SVG XML，讀取根元素的 `viewBox`：

```svg
<svg viewBox="0 0 131.57087 141.80041" ...>
```

即 SVG 寬 = 131.57, 高 = 141.80。

### 3. 遊戲座標 → SVG 像素

```python
svg_x = (game_x - bounds[0][0]) / (bounds[1][0] - bounds[0][0]) * svg_width
svg_y = (game_y - bounds[0][1]) / (bounds[1][1] - bounds[0][1]) * svg_height
```

> 若 `objective_gps.json` 中有預算的百分比，也可直接用：
> `svg_x = leftPercent / 100 * svg_width`
> `svg_y = topPercent / 100 * svg_height`

### 4. 樓層切換

SVG 中每個樓層是一個 `<g>` 元素：

```svg
<g id="Ground_Level"> ... </g>
<g id="First_Floor"> ... </g>
```

顯示指定樓層時，隱藏其他 `<g>`（`display: none`），
只顯示目標樓層的 `<g id="對應樓層">`。

### 5. 放置標記

在計算出的 `(svg_x, svg_y)` 位置上疊加一個標記元素。
可直接在 SVG 內插入一個圓點：

```svg
<circle cx="svg_x" cy="svg_y" r="3" fill="red" />
```

或在前端用 CSS/Canvas 疊加。

### 6. 渲染方式

| 方式 | 說明 |
|---|---|
| **Web 瀏覽器** | 直接嵌入 SVG 標籤 + JavaScript 操作 DOM，最簡單 |
| **Python + Pillow/Cairo** | 將 SVG 柵格化為圖片，再用 Pillow 畫標記 |
| **Python + svg.py** | 直接操作 SVG 文本，插入 `<circle>` 後儲存 |
| **QT / WPF** | 用 SVG 渲染元件 + 圖層疊加 |

---

## bounds 詳解

`bounds` 定義了遊戲世界座標到 SVG 畫布的映射矩形，是本功能的核心：

```json
"bounds": [[x1, y1], [x2, y2]]
```

| 值 | 意義 |
|---|---|
| `bounds[0]` = `[x1, y1]` | SVG 左上角對應的遊戲座標 |
| `bounds[1]` = `[x2, y2]` | SVG 右下角對應的遊戲座標 |

### 映射關係示意

```
遊戲世界                         SVG 畫布
(x1, y1) ─────────── (x2, y1)    (0, 0) ───────── (svg_w, 0)
    │                           │
    │    線性對應                   │
    │                           │
(x1, y2) ─────────── (x2, y2)    (0, svg_h) ──── (svg_w, svg_h)
```

### 邊界值不一定是 min/max

`bounds[0]` 和 `bounds[1]` 並非保證 `x1 < x2` 或 `y1 < y2`。
例如 Factory：

```json
"bounds": [[-67, 69], [76.6, -65.5]]
```

- x 從 -67 → 76.6（遞增，正常）
- y 從 69 → -65.5（遞減，SVG Y 軸向下為正，遊戲 Z 軸向上為正）

轉換公式中的分母 `(bounds[1][0] - bounds[0][0])` 和
`(bounds[1][1] - bounds[0][1])` 會自然處理正負號：

```python
# x1=-67, x2=76.6  →  分母 = 143.6 (正數)
# y1=69, y2=-65.5  →  分母 = -134.5 (負數，Y 軸反轉)
svg_x = (game_x - (-67)) / 143.6 * svg_w
svg_y = (game_y - 69) / (-134.5) * svg_h  # Y 自動反轉
```

### bounds 資料來源

這些數值由社群透過以下方式測定：
1. 在遊戲中走到地圖的極限邊緣位置
2. 截圖取得座標（檔名內嵌 x, z 值）
3. 將邊緣座標對應到 SVG 的可見範圍

### 與 objective_gps.json 的關係

`objective_gps.json` 中的 `leftPercent` / `topPercent` 本質上是 bounds 的預算結果：

```
leftPercent = (game_x - bounds[0][0]) / (bounds[1][0] - bounds[0][0]) * 100
topPercent  = (game_y - bounds[0][1]) / (bounds[1][1] - bounds[0][1]) * 100
```

若已有百分比，可直接用 `leftPercent / 100 * svg_w` 得到 SVG X 座標，
無需再次計算 bounds。

---

## 完整流程範例（Python 概念）

```python
import xml.etree.ElementTree as ET
import json

# 1. 載入 maps.json
with open("maps.json") as f:
    maps = json.load(f)

# 2. 選定地圖
map_name = "factory"
map_data = maps[map_name]
svg_file = f"maps/{map_data['svg']['file']}"
bounds = map_data['svg']['bounds']
floors = map_data['svg']['floors']

# 3. 解析 SVG viewBox
tree = ET.parse(svg_file)
root = tree.getroot()
_, _, svg_w, svg_h = map(float, root.get("viewBox").split())

# 4. 遊戲座標轉換
game_x, game_y = 10.0, 20.0  # 從截圖檔名解析得來
svg_x = (game_x - bounds[0][0]) / (bounds[1][0] - bounds[0][0]) * svg_w
svg_y = (game_y - bounds[0][1]) / (bounds[1][1] - bounds[0][1]) * svg_h

# 5. 樓層控制
target_floor = "Ground_Floor"
for g in root.findall(".//{http://www.w3.org/2000/svg}g"):
    g.set("display", "none" if g.get("id") != target_floor else "inline")

# 6. 插入標記
ns = "http://www.w3.org/2000/svg"
marker = ET.SubElement(root, f"{{{ns}}}circle")
marker.set("cx", str(svg_x))
marker.set("cy", str(svg_y))
marker.set("r", "4")
marker.set("fill", "red")

# 7. 儲存結果
tree.write("output.svg")
```

---

## 注意事項

- **座標旋轉**：`coordinateRotation` 表示 SVGs 的旋轉角度。部分地圖（如工廠 90°、海關 180°）的 SVG 已按此角度繪製，`bounds` 已配合旋轉後的座標系定義，因此轉換時不需額外處理旋轉。
- **遊戲座標取得**：座標可從 EFT 截圖檔名解析（`x, z` 即地圖平面座標），或從 `objective_gps.json` 取得任務目標百分比位置。
- **SVG 縮放**：若要在 UI 中顯示，SVG 可等比縮放，標記位置需按相同比例轉換。
