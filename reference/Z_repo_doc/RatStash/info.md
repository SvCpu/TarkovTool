# RatStash

.NET 開源函式庫，提供逃離塔科夫完整物品資料的解析與查詢能力，作為其他工具（如 RatEye、RatScanner）的物品資料庫層。

## 數據來源

### items.json（核心資料庫）

來源是**遊戲客戶端本身的內部物品資料庫**，與 EFT 遊戲檔案中的 `items.json` 結構完全相同。

每一筆條目以 24 字元的 BSG UID 為鍵，並依 `_type` 分為兩類：

```json
{
  "5a608bf24f39f98ffc77720e": {
    "_id": "5a608bf24f39f98ffc77720e",
    "_name": "Item",
    "_parent": "5447e1d04bdc2dff2f8b4569",
    "_type": "Node",         // ← Node：分類節點（無 _props）
    "_props": { ... }
  },
  "5447a9cd4bdc2dbd208b4567": {
    "_id": "5447a9cd4bdc2dbd208b4567",
    "_name": "AssaultRifle",
    "_parent": "5422acb9af1c889c16000029",
    "_type": "Item",         // ← Item：實際物品（含完整屬性 _props）
    "_props": {
      "Name": "Colt M4A1 5.56x45 assault rifle",
      "ShortName": "M4A1",
      "Weight": 3.49,
      "Width": 2,
      "Height": 1,
      "StackMaxSize": 1,
      ...
    }
  }
}
```

- **Node**：分類節點，透過 `_id` → `_parent` 構成樹狀類別層級
- **Item**：實際物品，`_parent` 指向一個 Node，表示該物品的類別

測試用的 `RatStashTest/TestData/items.json`（約 465,000 行）即為遊戲實際數據的副本。

### Locale 檔（在地化名稱）

`TestData/locales/{lang}.json` 提供各語言的物品名稱翻譯：

```json
{
  "5447a9cd4bdc2dbd208b4567 Name": "Colt M4A1 5.56x45 assault rifle",
  "5447a9cd4bdc2dbd208b4567 ShortName": "M4A1",
  "5447a9cd4bdc2dbd208b4567 Description": "The Colt M4A1 carbine..."
}
```

支援 18 種語言，載入後會覆蓋 items.json 中的 Name / ShortName / Description。

## 類別對應層（_name → C# Type）

透過 `Database.cs:156-279` 的 `NameToItemType()` 方法，將遊戲內部的 `_name` 字串對應到 C# 強型別類別：

- `"Weapon"` → `Weapon` class
- `"AssaultRifle"` → `AssaultRifle` class
- `"Armor"` → `Armor` class
- `"Backpack"` → `Backpack` class
- ...共約 120 種物品類別

解析分兩階段：
1. **第一遍**：掃描所有 Node，建立 `_id → C# Type` 映射表
2. **第二遍**：對每個 Item，根據其 `_parent` 查出對應 Type，將 `_props` JSON 反序列化為該型別的 C# 物件

## 主要功能

| 方法 | 用途 |
|---|---|
| `GetItem(id)` | O(1) 透過 BSG UID 查物品 |
| `GetItems(filter)` | 透過 Lambda 篩選物品 |
| `GetItem(ratingFunc)` | 依評分函數取最佳物品（適合 Levenshtein 模糊比對名稱） |
| `Filter(predicate)` | 建立子資料庫 |
| `IsNode(id)` | 檢查 UID 是否為節點 |

所有查詢回傳的 Item 物件皆經過 `DeepClone()`，確保外部修改不影響內部資料。

## 緩存索引解析（ParseItemCacheHashIndex）

README 中提及此功能，用於解析遊戲 Icon Cache 的 `index.json`，將數字索引（cache key）→ BSG UID → Item 物件。但此版本程式碼中**該方法尚未實作**。

## 遊戲數據提取

**此倉庫不包含任何從遊戲客戶端中提取/擷取數據的邏輯。**

它只做一件事：解析已經存在的靜態 JSON 檔案（`items.json` + locale 檔）。這些 JSON 檔必須由外部工具（例如從 EFT Unity 資源檔中手動解包）事先準備好，開發者再將它們放入 `TestData/` 目錄作為測試資料。`Database.FromFile()` 僅是單純的 JSON 反序列化，沒有連接遊戲、讀取遊戲檔案系統或記憶體的程式碼。

## 與 RatEye 的關係

- **RatStash**：純資料庫層，解析 items.json 提供物品查詢（O(1) UID 查找）
- **RatEye**：視覺識別層，將截圖辨識出的 UID 傳給 RatStash 取得物品資訊
