# eft-where-am-i 地圖圖像來源

地圖圖像及 UI 來自 **tarkov-market.com**（https://tarkov-market.com/）。

## 使用方式

**直接以嵌入式瀏覽器開啟網頁**，並非下載地圖到本地。

應用程式使用 Microsoft Edge WebView2 元件，在程式內建一個嵌入式瀏覽器，
直接導航至 `https://tarkov-market.com/maps/{地圖名稱}`，即時載入
tarkov-market.com 的網頁地圖及其 UI。

這種方式類似於在程式內部開啟一個專用的瀏覽器視窗來顯示網站內容，
因此地圖數據並沒有被下載到本地儲存，而是每次即時從網站載入。

（來源：`eft-where-am-i/UserControls/WhereAmI.cs:51`）

## 位置偵測原理

並非上傳圖像檔案，而是利用 EFT 遊戲截圖的**檔案名稱**來取得座標。

1. EFT 遊戲截圖時，會自動在 PNG 檔名中嵌入玩家座標資訊，
   格式為：`YYYY-MM-DD[HH-MM]_x, y, z_quatX, quatY, quatZ, quatW_speed`
   （例如：`2026-01-10[03-59]_-318.44, 24.84, -107.49_0.00000, 0.82497, 0.00000, 0.56518_3.98.png`）

2. 應用程式使用 `FileSystemWatcher` 監控 EFT 截圖資料夾，
   當新 PNG 檔案產生時自動觸發。

3. 程式僅讀取**檔案名稱字串**（不含副檔名），透過 JavaScript 注入
   （`SetInputValueAsync`）填入 tarkov-market.com 網站的輸入框中。

4. tarkov-market.com 網站內建的 "Where am I?" 功能會自動解析
   該字串中的 x, y, z 座標，並在地圖上放置位置標記。

5. 程式另會解析 Z 座標，自動切換地圖的樓層圖層。

**關鍵點：** 座標資料來源是遊戲寫入**檔名**的中繼資料，
程式僅讀取檔名字串並填入網頁輸入框，不涉及任何圖像上傳或網路傳輸。
（來源：`WhereAmI.cs:498-564`、`WhereAmI.cs:592-624`）

專案本身與 tarkov-market.com 無正式官方關聯。
（來源：README.md 第 21 行及 README_en.md 第 21 行，以及 Credits 章節）
