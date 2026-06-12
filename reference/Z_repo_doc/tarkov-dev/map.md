# tarkov-dev 地圖系統

## 1. 整體架構

```
src/
  data/
    maps.json              <-- 靜態配置：所有地圖屬性、邊界、圖層、標籤
    maps_static.json       <-- 遺留靜態標記數據（狙擊手 Scav 重生點等）
  features/
    maps/
      index.js             <-- Redux slice、map data 擷取 hooks、圖片合併邏輯
      do-fetch-maps.mjs    <-- API 查詢：動態標記（撤離點、戰利品、重生點等）
  pages/
    map/
      index.jsx            <-- 主要地圖頁面：Leaflet 初始化、SVG 載入、圖層切換、標記渲染
      index.css             <-- 圖層可見性 CSS（hidden-layer、off-level、base-layer、level-layer）
      map-images.mjs        <-- 標記類型對應的圖示檔名
    maps/
      index.jsx            <-- 地圖總覽列表頁面
  modules/
    leaflet-control-groupedlayer.js   <-- 自訂 Leaflet 圖層控制（支援分組）
    leaflet-control-coordinates.js    <-- 座標顯示與輸入
    leaflet-control-map-settings.js   <-- 設定面板
    leaflet-control-raid-info.js      <-- RAID 計時器 + 玩家人數
    leaflet-control-map-search.js     <-- 任務/物品/容器搜尋列
    leaflet-control-remote.js         <-- 遠端連線控制（未完成）
```

---

## 2. maps.json 結構（核心配置）

`src/data/maps.json` 是一個扁平陣列，每筆為一個「地圖組」（一個地圖名稱如 `customs`、`streets-of-tarkov`），每個組包含 `maps[]` 陣列，內含多個變體（interactive、2D、3D）。

### 地圖組結構

```json
{
    "normalizedName": "streets-of-tarkov",
    "primaryPath": "/map/streets-of-tarkov",
    "maps": [
        {
            "key": "streets-of-tarkov",
            "projection": "interactive",
            "minZoom": 1,
            "maxZoom": 5,
            "transform": [0.38, 0, 0.38, 0],
            "coordinateRotation": 180,
            "bounds": [
                [323, -295],
                [-280, 532]
            ],
            "author": "Shebuka",
            "authorLink": "https://github.com/the-hideout/tarkov-dev-svg-maps/",
            "svgPath": "https://assets.tarkov.dev/maps/svg/StreetsOfTarkov.svg",
            "svgLayer": "Ground_Level",
            "heightRange": [-6, 10],
            "layers": [ /* 樓層定義 */ ],
            "labels": [ /* 地名標註 */ ]
        },
        {
            "key": "streets-2d",  "projection": "2D", ...
        },
        {
            "key": "streets-3d",  "projection": "3D", ...
        }
    ]
}
```

### Interactive 地圖關鍵欄位

| 欄位 | 型別 | 說明 |
|---|---|---|
| `key` | string | 唯一標識符（用於 URL `/map/{key}`） |
| `projection` | `"interactive"` | 標記此為 Leaflet 互動版本 |
| `transform` | `[scaleX, offsetX, scaleY, offsetY]` | 遊戲座標 → Leaflet CRS 的仿射變換 |
| `coordinateRotation` | number (0/90/180/270) | 座標系統旋轉角度，對齊 SVG 地圖方向 |
| `bounds` | `[[maxX, minZ], [minX, maxZ]]` | 地圖在遊戲座標中的邊界 |
| `svgPath` | URL | SVG 檔案網址（由 assets.tarkov.dev 提供） |
| `svgLayer` | string (如 `"Ground_Level"`) | SVG 中 `<g id="...">` 基底圖層 |
| `heightRange` | `[minHeight, maxHeight]` | 基底圖層的高度範圍 |
| `tilePath` | URL template | 可選的衛星圖磚路徑 |
| `tileSize` | number | 圖磚大小（預設 256） |
| `altMaps` | string[] | 共享此配置的替代地圖 key |
| `svgBounds` | `[[maxX, minZ], [minX, maxZ]]` | 可選的 SVG 覆蓋邊界（不同於 `bounds`） |
| `layers` | array | 樓層定義（SVG group 名稱 + 高度範圍） |
| `labels` | array | 文字標註 |

---

## 3. 樓層/圖層切換機制

### 3a. maps.json 中的樓層定義

`layers` 陣列的每筆：

```json
{
    "name": "Underground",
    "svgLayer": "Underground_Level",
    "tilePath": "https://...",
    "show": false,
    "extents": [
        {
            "height": [-10000, -6],
            "bounds": [
                [[x1, z1], [x2, z2], "label"]
            ]
        }
    ]
}
```

- `extents.height`：該樓層的遊戲 Y（高度）範圍 `[min, max)`
- `extents.bounds`：可選的子區域邊界（用於僅部分區域有多層的地圖）
- `svgLayer`：對應 SVG 中的 `<g id="svgLayer">`

### 3b. SVG 圖層解析與切換

載入 SVG 時 (`index.jsx ~862-901`)：

```js
// 取得 SVG 文字內容
svgLoaded = fetch(mapData.svgPath)
    .then((response) => response.text())
    .then((svgText) => {
        svgElement.innerHTML = svgText;
        const layerGroups = [...svgElement.children[0].children]
            .filter((c) => c.nodeName === "g" && !!c.id);
        // 將 svgLayer 設為 base-layer，其他設為 hidden-layer overlay-layer
        for (const layerGroup of layerGroups) {
            if (layerGroup.id === mapData.svgLayer ||
                layerGroup.dataset["keepWithGroup"] === mapData.svgLayer) {
                layerGroup.classList.add("base-layer");
            } else {
                layerGroup.classList.add("hidden-layer", "overlay-layer");
            }
        }
    });
```

切換樓層時（`index.jsx ~990-1021`）：

```js
heightLayer.on("add", () => {
    baseLayer._image.classList.add("off-level");  // 調暗基底
    // 隱藏所有非該樓層的 SVG group，顯示該樓層
    for (const layerGroup of baseLayer._image.children[0].children) {
        if (layerGroup.id !== layer.svgLayer) {
            layerGroup.classList.add("hidden-layer");
            continue;
        }
        layerGroup.classList.remove("hidden-layer");
    }
});
```

CSS 控制可見性：

```css
.leaflet-pane svg .overlay-layer.hidden-layer { display: none; }
.leaflet-pane svg.auto-show .overlay-layer.hidden-layer { display: block; }
```

### 3c. Exclusive Group（單選）

圖層控制使用 `exclusiveOptionalGroups: ["Levels"]`，同一時間只能啟用一個樓層（radio button 行為）。

### 3d. Ctrl + 滾輪快速切換

`index.jsx ~605-653` 實作了 Ctrl+滑鼠滾輪上下循環切換樓層。

---

## 4. 座標轉換（遊戲座標 → Leaflet 像素）

### 4a. 自訂 CRS

```js
function getCRS(mapData) {
    let scaleX = 1, scaleY = 1, marginX = 0, marginY = 0;
    if (mapData?.transform) {
        scaleX = mapData.transform[0];
        scaleY = mapData.transform[2] * -1;  // Y 軸反轉（遊戲 Y↑ → Leaflet Y↓）
        marginX = mapData.transform[1];
        marginY = mapData.transform[3];
    }
    return L.extend({}, L.CRS.Simple, {
        transformation: new L.Transformation(scaleX, marginX, scaleY, marginY),
        projection: L.extend({}, L.Projection.LonLat, {
            project: (latLng) => L.Projection.LonLat.project(
                applyRotation(latLng, mapData.coordinateRotation)),
            unproject: (point) => applyRotation(
                L.Projection.LonLat.unproject(point), mapData.coordinateRotation * -1),
        }),
    });
}
```

### 4b. 旋轉函數

```js
function applyRotation(latLng, rotation) {
    const angleRad = (rotation * Math.PI) / 180;
    const cos = Math.cos(angleRad), sin = Math.sin(angleRad);
    const { lng: x, lat: y } = latLng;
    return L.latLng(x * sin + y * cos, x * cos - y * sin);
}
```

### 4c. 軸對換

遊戲中 `(x, y, z)` → Leaflet `[lat, lng]` = `[z, x]`，y（高度）用於樓層過濾。

```js
function pos(position) {
    return [position.z, position.x];  // → [lat, lng]
}
```

### 4d. 完整轉換管線

```
遊戲座標 (x, z)
  → Leaflet [lat=z, lng=x]       (pos())
  → 旋轉 coordinateRotation 度    (applyRotation)
  → Leaflet CRS.Simple 投影        (無投影，直接作為像素)
  → L.Transformation 變換          (scale + offset)
  → 螢幕像素位置
```

### 4e. bounds 轉換

```json
"bounds": [[maxX, minZ], [minX, maxZ]]
```

```js
function getBounds(bounds) {
    return L.latLngBounds(
        [bounds[0][1], bounds[0][0]],  // SW: [minZ, maxX]
        [bounds[1][1], bounds[1][0]]   // NE: [maxZ, minX]
    );
}
```

### 4f. Markers 可見性過濾

```js
function markerIsOnLayer(marker, layer) {
    if (!layer?.options?.extents) return true;
    const top = marker.options.top || marker.options.position.y;
    const bottom = marker.options.bottom || marker.options.position.y;
    for (const extent of layer.options.extents) {
        if (top >= extent.height[0] && bottom < extent.height[1]) {
            if (extent.bounds) {
                // 檢查 sub-region 邊界
                for (const ba of extent.bounds) {
                    if (getBounds(ba).contains(pos(marker.options.position)))
                        return "full";
                }
            } else {
                return "full";
            }
        }
    }
    return false;
}
```

不活動的 marker 獲得 `off-level` CSS（`opacity: 0.2; z-index: -9999`）。

---

## 5. 各圖層在不同地圖的 transform 與 rotation

| 地圖 | transform | rotation | 說明 |
|---|---|---|---|
| Streets of Tarkov | `[0.38, 0, 0.38, 0]` | 180 | |
| Ground Zero | `[0.524, 167.3, 0.524, 65.1]` | 180 | |
| Customs | `[0.239, 168.65, 0.239, 136.35]` | 180 | |
| Factory | `[1.629, 119.9, 1.629, 139.3]` | 90 | 旋轉 90 度 |
| Interchange | `[0.265, 150.6, 0.265, 134.6]` | 180 | |
| Laboratory | `[0.575, 281.2, 0.575, 193.7]` | 270 | 旋轉 270 度 |
| Reserve | `[0.395, 122.0, 0.395, 137.65]` | 180 | |
| Shoreline | `[0.16, 83.2, 0.16, 111.1]` | 180 | |
| Woods | `[0.1855, 112.95, 0.1855, 167.85]` | 180 | |
| Lighthouse | `[0.2, 0, 0.2, 0]` | 180 | |
| Terminal | `[0.20, 0, 0.20, 0]` | 180 | |
| Labyrinth | `[2.115, 85.5, 2.115, 128.0]` | 270 | 旋轉 270 度 |

---

## 6. 兩種底圖：衛星 vs 抽象

- **衛星圖**：`tilePath` 指向 `assets.tarkov.dev/maps/{map}/{version}/{z}/{x}/{y}.png`（預渲染 PNG 圖磚）
- **抽象圖**：`svgPath` 指向 `assets.tarkov.dev/maps/svg/{MapName}.svg`（向量 SVG，來源：`the-hideout/tarkov-dev-svg-maps` 倉庫）

兩者透過 Leaflet base layer 切換。

---

## Python 等效參考程式碼

```python
"""
tarkov-dev 地圖系統的 Python 等效實作參考。

包含：
1. 遊戲座標 → 像素座標的仿射變換
2. SVG 圖層管理（多樓層切換）
3. 動態標記過濾
"""

import math
import json
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field


# ──────────────────────────────────────────────
# 資料模型（對應 maps.json 結構）
# ──────────────────────────────────────────────

@dataclass
class MapExtent:
    height: list[float]  # [min, max)
    bounds: Optional[list] = None  # 可選 sub-region

@dataclass
class MapLayer:
    name: str
    svgLayer: str
    show: bool = False
    tilePath: Optional[str] = None
    extents: list[MapExtent] = field(default_factory=list)

@dataclass
class InteractiveMap:
    key: str
    transform: list[float]  # [scaleX, offsetX, scaleY, offsetY]
    coordinateRotation: int  # 0, 90, 180, 270
    bounds: list  # [[maxX, minZ], [minX, maxZ]]
    svgPath: str
    svgLayer: str
    heightRange: list[float]
    layers: list[MapLayer] = field(default_factory=list)
    labels: list = field(default_factory=list)
    minZoom: int = 1
    maxZoom: int = 5
    tilePath: Optional[str] = None
    altMaps: list[str] = field(default_factory=list)


# ──────────────────────────────────────────────
# 座標轉換（遊戲座標 → 像素座標）
# ──────────────────────────────────────────────

class CoordinateTransformer:
    """
    模仿 Leaflet CRS.Simple + L.Transformation + coordinateRotation。
    
    遊戲座標系：(x, y, z)  其中 y 為高度
    Pixel 座標系：[col, row] (x向右, y向下)
    """
    
    def __init__(self, transform: list[float], rotation: int = 0):
        self.scale_x = transform[0]
        self.offset_x = transform[1]
        # Y 軸反轉：遊戲 Y↑ → 像素 Y↓
        self.scale_y = transform[2] * -1
        self.offset_y = transform[3]
        self.rotation = rotation
    
    def _rotate(self, x: float, z: float) -> tuple[float, float]:
        """對 (lng=x, lat=z) 進行旋轉"""
        angle = math.radians(self.rotation)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        # 公式對應 Leaflet:
        # rotatedX = x * cos - z * sin
        # rotatedY = x * sin + z * cos
        rx = x * cos_a - z * sin_a
        rz = x * sin_a + z * cos_a
        return rx, rz
    
    def game_to_pixel(self, x: float, z: float) -> tuple[float, float]:
        """
        將遊戲 (x, z) 轉換為像素 (col, row)。
        
        管線：
          1. Leaflet [lat=z, lng=x]  → 傳入 (lng=x, lat=z)
          2. 旋轉 (lng, lat)
          3. L.Transformation:
             pixelX = scaleX * lng + offsetX
             pixelY = scaleY * lat + offsetY   (scaleY 已反轉)
        """
        lng, lat = self._rotate(x, z)
        px = self.scale_x * lng + self.offset_x
        py = self.scale_y * lat + self.offset_y
        return px, py
    
    def pixel_to_game(self, px: float, py: float) -> tuple[float, float]:
        """反向轉換：像素 → 遊戲 (x, z)"""
        lng = (px - self.offset_x) / self.scale_x
        lat = (py - self.offset_y) / self.scale_y
        x, z = self._rotate(lng, lat)
        return x, z


# ──────────────────────────────────────────────
# SVG 圖層管理
# ──────────────────────────────────────────────

from xml.etree import ElementTree as ET

class SvgLayerManager:
    """
    管理 SVG 中各 <g> 圖層的可見性。
    對應 index.jsx 中的 layerGroups.classList 切換。
    """
    
    def __init__(self, svg_path: str, base_layer_id: str):
        self.tree = ET.parse(svg_path)
        self.root = self.tree.getroot()
        self.base_layer_id = base_layer_id
        # 命名空間處理（SVG 通常有 xmlns）
        self.ns = {"svg": "http://www.w3.org/2000/svg"}
        self._init_layers()
    
    def _init_layers(self):
        """初始化所有圖層：基底顯示，其他隱藏"""
        for g in self.root.findall(".//svg:g", self.ns):
            gid = g.get("id", "")
            if gid == self.base_layer_id:
                g.set("class", "base-layer")
            elif gid:
                g.set("class", "hidden-layer overlay-layer")
    
    def show_layer(self, layer_id: str):
        """顯示指定圖層，隱藏其他所有圖層"""
        for g in self.root.findall(".//svg:g", self.ns):
            gid = g.get("id", "")
            classes = (g.get("class") or "").split()
            if gid == layer_id:
                classes = [c for c in classes if c != "hidden-layer"]
                g.set("class", " ".join(classes))
            elif gid:
                if "hidden-layer" not in classes:
                    classes.append("hidden-layer")
                g.set("class", " ".join(classes))
    
    def show_base(self):
        """恢復基底圖層，隱藏所有 overlay 圖層"""
        for g in self.root.findall(".//svg:g", self.ns):
            gid = g.get("id", "")
            classes = (g.get("class") or "").split()
            if gid == self.base_layer_id:
                classes = [c for c in classes if c != "hidden-layer"]
            elif gid:
                if "hidden-layer" not in classes:
                    classes.append("hidden-layer")
            g.set("class", " ".join(classes))
    
    def export(self, path: str):
        """匯出修改後的 SVG（保持原始格式）"""
        self.tree.write(path, encoding="utf-8", xml_declaration=True)


# ──────────────────────────────────────────────
# 動態標記過濾（依當前樓層）
# ──────────────────────────────────────────────

@dataclass
class MapMarker:
    position: dict  # {"x": float, "y": float, "z": float}
    top: Optional[float] = None
    bottom: Optional[float] = None
    marker_type: str = ""


class MarkerFilter:
    """
    根據當前啟用樓層決定哪些 marker 可顯示。
    對應 index.jsx 的 markerIsOnLayer / markerIsOnActiveLayer。
    """
    
    @staticmethod
    def is_on_layer(marker: MapMarker, layer: MapLayer) -> bool:
        if not layer.extents:
            return True
        
        marker_top = marker.top if marker.top is not None else marker.position["y"]
        marker_bottom = marker.bottom if marker.bottom is not None else marker.position["y"]
        marker_pos = (marker.position["x"], marker.position["z"])
        
        for extent in layer.extents:
            h_min, h_max = extent.height
            if marker_top >= h_min and marker_bottom < h_max:
                if extent.bounds:
                    for bound_entry in extent.bounds:
                        bbox = bound_entry  # [[maxX, minZ], [minX, maxZ]]
                        sw = (bbox[0][0], bbox[0][1])  # (maxX, minZ)
                        ne = (bbox[1][0], bbox[1][1])  # (minX, maxZ)
                        if MarkerFilter._point_in_bounds(marker_pos, sw, ne):
                            return True
                else:
                    return True
        return False
    
    @staticmethod
    def _point_in_bounds(
        point: tuple[float, float],
        sw: tuple[float, float],
        ne: tuple[float, float]
    ) -> bool:
        """檢查點是否在邊界內（對應 L.latLngBounds.contains）"""
        px, pz = point
        max_x, min_z = sw
        min_x, max_z = ne
        return min_x <= px <= max_x and min_z <= pz <= max_z


# ──────────────────────────────────────────────
# 使用範例
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # 載入 maps.json
    with open("src/data/maps.json", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    # 找到 Streets of Tarkov 的 interactive 配置
    streets_group = next(
        g for g in raw_data if g["normalizedName"] == "streets-of-tarkov"
    )
    streets_config = next(
        m for m in streets_group["maps"] if m["projection"] == "interactive"
    )
    
    # 座標轉換
    xf = CoordinateTransformer(streets_config["transform"], streets_config["coordinateRotation"])
    
    # 測試：遊戲座標 → 像素
    pixel = xf.game_to_pixel(150, -100)
    print(f"Game (150, -100) → Pixel {pixel}")
    
    # Python 等效 bounds 轉換
    bounds = streets_config["bounds"]
    sw = [bounds[0][1], bounds[0][0]]  # [minZ, maxX]
    ne = [bounds[1][1], bounds[1][0]]  # [maxZ, minX]
    print(f"Bounds SW: {sw}, NE: {ne}")
    
    # 圖層過濾
    marker = MapMarker(
        position={"x": 100, "y": -2, "z": 50},
        top=-1, bottom=-3
    )
    layer_def = streets_config["layers"][0]
    layer = MapLayer(
        name=layer_def["name"],
        svgLayer=layer_def["svgLayer"],
        show=layer_def.get("show", False),
        extents=[MapExtent(**e) for e in layer_def["extents"]]
    )
    visible = MarkerFilter.is_on_layer(marker, layer)
    print(f"Marker on layer '{layer.name}': {visible}")
```

---

## 相關檔案

| 檔案 | 用途 |
|---|---|
| `src/data/maps.json` | 所有地圖配置：邊界、變換、圖層、標籤 |
| `src/pages/map/index.jsx` | 主要地圖元件：Leaflet 初始化、SVG 載入、CRS 設定、圖層切換、標記渲染 |
| `src/pages/map/index.css` | 圖層可見性 CSS |
| `src/modules/leaflet-control-groupedlayer.js` | 自訂分組圖層控制（支援獨佔群組） |
| `src/features/maps/index.js` | Redux slice、`useMapImages()` 合併靜態配置與 API 資料 |
| `src/features/maps/do-fetch-maps.mjs` | 從 API 獲取動態標記（撤離點、戰利品、重生點等） |
| `src/pages/map/map-images.mjs` | 標記類型對應的圖示名稱 |
