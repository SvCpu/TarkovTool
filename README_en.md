This document was translated into English using AI. Please refer to the original README.md (Chinese version) as the authoritative source.

# Tarkov Tool

An [Escape from Tarkov][escape-from-tarkov] tool library

Language: [繁體中文](README.md)/[Eng(ai translate)](README_en.md)/...

# Data
## Tarkov Sensitive Data
This project will hash Tarkov sensitive data by default to protect privacy
This behavior is controlled by the class attribute `tarkov_tool.config.Config.enable_sensitive_data_hashing_for_tarkov`

Tarkov sensitive data includes but is not limited to:
 - AccountID
 - ProFileID

>[!NOTE]
>This behavior is designed to hash data upon reading and parsing before output

# References
[Escape from Tarkov [Sound Effects]](https://www.youtube.com/playlist?list=PLq44zq7R2Kq7mUiGSXXjkcjHR7EDzHo6L)
[Escape from Tarkov Wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki)
[Tarkov GraphQL API](https://api.tarkov.dev/)

## Copyright Notice
### MindEscape Font
```
assets/font/MindEscape.ttf
```
A font that looks like Tarkov Time

From [onlinewebfonts](http://www.onlinewebfonts.com)

Website Copyright Notice
```html
<div>Fonts made from <a href="http://www.onlinewebfonts.com">Web Fonts</a> is licensed by CC BY 4.0</div>
```

>[!IMPORTANT]
>This project will automatically download files from other GitHub projects at runtime. Please follow their license terms when using them.

# License
Copyright (c) 2026 SvCpu
This project is licensed under GNU LGPL v3 - see the [LICENSE](./License) file for details

> [!CAUTION]
>This project is not affiliated with BSG/Battlestate Games
>
>The developers are not responsible for any in-game penalties, account bans, or other consequences resulting from the use of this tool library
>
>Although based on the tool library's operational principles, it should not cause any consequences
>
>Use at your own risk


[escape-from-tarkov]: https://www.escapefromtarkov.com/
