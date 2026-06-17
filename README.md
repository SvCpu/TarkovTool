# Tarkov Tool

一個[Escape from Tarkov][escape-from-tarkov]工具庫

Language: [繁體中文](README.md)/[Eng(ai translate)](README_en.md)/...

# 數據
## Tarkov 敏感數據
本項目默認會對讀取到的 Tarkov 敏感數據 進行哈希處理, 以保障隱私
這一行為由類屬性 `tarkov_tool.config.Config.enable_sensitive_data_hashing_for_tarkov` 控制

Tarkov 敏感數據包括但不限於:
 - AccountID
 - ProFileID

>[!NOTE]
>這一行為被設計成讀取到數據並解析時就會進行哈希處理再輸出

# 術語
|名稱|術語說明|補充|
|-|-|-|
|Game Session|指遊戲進程的一個完整生命週期. 從遊戲開始到結束(進程結束也為結束)算是一個 Session||
|Raid|指遊戲內的一場戰局. 通常是玩家進入地圖, 完成任務或戰鬥, 撤離後的過程|轉移到另外一個地圖後即使raid_id不同在也會被當成是同一個戰局(根據任務對同一個戰局的判定)|
|Raid Session|指一場 Raid 的組成部分, 這個術語用來描述「同一場戰局的不同片段」|由於可能出現斷線重連, 地圖轉移等情況, 會導致同一場 Raid 被分割成多個 Session. |
|Raid Group|指一場戰局作為隊友共同進入的小隊的成員|可能因服務器問題導致實際成員與log記錄的成員不符|

> 基於已有情況的記錄，以上術語有以下關係
> 
> 一個Raid由一個或多個Raid Session組成
> 
> 一般情況下Raid只會有一個對應的Raid Group; 如果有地圖轉移, 可能會有不同的Raid Group
> 
> 同一場 Raid 可能跨越不同的 Game Session, 例如因玩家主動重啟遊戲或遊戲意外退出

# 引用
[Escape from Tarkov [Sound Effects]](https://www.youtube.com/playlist?list=PLq44zq7R2Kq7mUiGSXXjkcjHR7EDzHo6L)
[Escape from Tarkov Wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki)
[Tarkov GraphQL API](https://api.tarkov.dev/)

## 版權說明
### MindEscape字體
```
assets/font/MindEscape.ttf
```
一款好似塔克夫Time嘅字體

來自[onlinewebfonts](http://www.onlinewebfonts.com)

網站的版權要求
```html
<div>Fonts made from <a href="http://www.onlinewebfonts.com">Web Fonts</a> is licensed by CC BY 4.0</div>
```

>[!IMPORTANT]
>本專案在運行時會自動下載其他GitHub項目檔案，使用時需遵循其授權條款

# 授權條款
Copyright (c) 2026 SvCpu
本專案採用 GNU LGPL v3 授權條款 - 詳見 [LICENSE](./License) 文件

> [!CAUTION]
>本專案與BSG/Battlestate Games無關
>
>開發者不承擔因使用工具庫而產生的任何遊戲內懲罰、封號或其他後果
>
>儘管根據工具庫運行原理不應該造成任何後果
>
>使用風險自負


[escape-from-tarkov]: https://www.escapefromtarkov.com/