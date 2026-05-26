# carlsmei_tarkovdata

從 Tarkov 後端 API 直接收集的原始數據倉庫，由機器人維護，每 12 小時更新一次。

- 授權：Unlicense（公有領域）
- 遊戲版本：`1.0.2.0.43037`

---

## JSON 資料結構

### 頂層

- **`items.json`** (`Dict[str, Item]`) — 完整物品資料庫，以 BSG UID 為鍵。結構與 RatStash 相同，包含 `_type: "Node"`（分類節點）與 `_type: "Item"`（實際物品）兩種條目，`_props` 依物品類別有不同屬性集合。
- **`items-prices.json`** (`Dict[str, int]`) — 物品跳蚤市場最低價格，UID → 價格（盧布）。
- **`customization.json`** (`Dict[str, Customization]`) — 角色外觀自定義資料，以 UID 為鍵。包含服裝套裝、身體部位、手勢等 Node/Item 層級結構。
- **`locations.json`** (`{"locations": Dict[str, Location]}`) — 地圖/戰區設定，包含 Bot 生成參數、撤離時間、玩家數量限制、Heatmap 圖層配置等。
- **`globals.json`** (`{"config": Dict[str, any]}`) — 全域遊戲設定，包含瞄準機制、空投參數、護甲材料屬性、技能經驗曲線、體力/耐力設定等。
- **`distrib.json`** (單一物件) — 遊戲客戶端發行資訊，包含版本、雜湊值、下載 URI、Torrent URI、所需磁碟空間。
- **`ending.json`** (`{"elements": List[Ending]}`) — 遊戲結局/成就定義，包含條件（任務/等級要求）與獎勵（外觀解鎖）。
- **`prestige.json`** (`{"elements": List[Prestige]}`) —  prestige（巔峰）系統定義，包含升級條件（等級、任務完成）與獎勵。
- **`tapes.json`** (`List[Tape]`) — 遊戲內錄音帶（tape）資料，包含錄音 ID 與其字幕時間軸（start/end 秒數）。
- **`subtitle-track.json`** (`List[SubtitleTrack]`) — 字幕軌道資料，包含字幕 ID 與時間軸。
- **`game_version.txt`** — 當前遊戲版本號字串。
- **`launcher_version.txt`** — 啟動器版本號字串。

### 子目錄

- **`achievements/list.json`** (`{"elements": List[Achievement]}`) — 成就定義，包含 ID、圖示 URL、獎勵列表、解鎖條件（擊殺特定 Scav 類型、達到等級等）。
- **`achievements/statistic.json`** (`{"elements": Dict[str, float]}`) — 成就完成統計百分比，成就 ID → 完成率（如 `"6529097eccf6aa5f8737b3d0": 0.05` 表示 0.05% 玩家完成）。

- **`hideout/areas.json`** (`List[HideoutArea]`) — 藏身處區域定義，包含類型 ID、各等級的建造需求、獎勵、插槽數。
- **`hideout/recipes.json`** (`{"recipes": List[Recipe]}`) — 藏身處製作配方，包含所需材料（物品/區域等級）、生產時間、產出物品。
- **`hideout/settings.json`** (單一物件) — 藏身處全局參數：發電機空轉速度、燃油流速、空氣濾清器流速、GPU 加速率。
- **`hideout/qte.json`** (`List[QTE]`) — 藏身處快速反應事件設定，包含類型（ShrinkingCircle）、按鍵、位置、速度、成功範圍。
- **`hideout/customization.json`** (`{"globals": List[HideoutCustomization]}`) — 藏身處裝飾自定義，包含地板、天花板、射擊標記等裝飾品及其解鎖條件。

- **`trading/settings.json`** (`List[Trader]`) — 商人設定，包含名稱、貨幣、忠誠度等級（等級/銷售額/聲望需求）、維修與保險設定。
- **`trading/customization/offers-bear.json`** (`List[CustomizationOffer]`) — BEAR 陣營外觀購買選項，包含商人 ID、套裝 ID、忠誠度/等級/任務需求。
- **`trading/customization/offers-usec.json`** (`List[CustomizationOffer]`) — USEC 陣營外觀購買選項，結構同上。
- **`trading/customization/storage.json`** (`List[CustomizationStorage]`) — 外觀物品庫存記錄，包含來源（preorder/event）與類型（suite/floor/ceiling 等）。

- **`dialogue/list.json`** (`{"elements": List[Dialogue]}`) — 對話樹定義，包含對話行、觸發條件（變數值比對）、動作（切換對話/設定變數）、動畫與字幕關聯。

- **`languages/*.json`** (`Dict[str, str]`) — 20 種語言的在地化翻譯檔，鍵為 `{UID} Name` / `{UID} ShortName` / `{UID} Description`。
