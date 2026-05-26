# tarkov-dev

[tarkov.dev](https://tarkov.dev) 官方網站的源碼。
使用 React 構建的前端專案。

提供逃離塔科夫的全面資訊，包括物品查詢、以物易物配方、
跳蚤市場價格、任務指南、地圖、藏身處利潤計算等功能。

---

## 互動地圖

使用 **Leaflet** + 自訂 CRS（座標參考系統）構建。

遊戲 `{ x, y, z }` 三維座標映射為 Leaflet 的 `[z, x]`（lat = z, lng = x），
每個地圖有 `transform` 矩陣 `[scaleX, marginX, scaleY, marginY]` 轉換遊戲座標到地圖座標。

### 兩種底圖選項

#### 1. 衛星圖（Satellite）

使用 **PNG 瓦片（tiles）**，從 `https://assets.tarkov.dev/maps/{mapName}/{z}/{x}/{y}.png` 載入。

由社群貢獻者從遊戲內截圖處理拼接而成，呈現接近遊戲實際視角的圖像。
每個地圖可有多個樓層子圖層（如 `main`、`underground`、`2nd` 等），各自有獨立的 tilePath。

```js
// 設定範例（maps.json）
"tilePath": "https://assets.tarkov.dev/maps/customs_0.16/main/{z}/{x}/{y}.png"
```

#### 2. 抽象圖（Abstract）

使用 **SVG 向量圖**，從 `https://assets.tarkov.dev/maps/svg/{MapName}.svg` 載入。

原始碼維護於 GitHub 倉庫 [the-hideout/tarkov-dev-svg-maps](https://github.com/the-hideout/tarkov-dev-svg-maps)。

渲染方式（`index.jsx:873-901`）：
1. `fetch()` 載入 SVG 字串
2. 注入到記憶體中的 `<svg>` 元素
3. 遍歷 SVG 的頂層 `<g>` 群組，根據 `id` 比對 `svgLayer`：
   - 匹配的群組加上 `base-layer` class（顯示）
   - 不匹配的加上 `hidden-layer overlay-layer` class（隱藏，可透過圖層控制切換）
4. 透過 `L.svgOverlay()` 將 SVG 疊加到 Leaflet 地圖上

```
底圖選擇（index.jsx:905-908）：
  tileLayer → tMaps("Satellite")    ← Leaflet L.tileLayer
  svgLayer  → tMaps("Abstract")     ← Leaflet L.svgOverlay
```

兩種底圖僅在同時有 `tilePath` 和 `svgPath` 的地圖上提供切換選項；
僅有 `svgPath` 的地圖（如 Streets of Tarkov）固定顯示抽象圖。
