# Tarkov Tool(WIP)

An [Escape from Tarkov][escape-from-tarkov] tool library

Language: [繁體中文](README.md)/[Eng(ai translate)](README_en.md)/...

> This document was translated into English using AI. Please refer to the original README.md (Chinese version) as the authoritative source.

# About
This project was initially created to learn Python and explore Tarkov's log information (who would have thought logs could be several GB).

The project is still in development, with no usage documentation yet.

The predecessor of this project is [TarkovParser](https://github.com/SvCpu/TarkovParserArchive)

# Currently Implemented
 - Calculate in-game Tarkov time based on real time (src/tarkov_tool/tarkov_time.py)
 - Get Tarkov-related file paths (scripts/print_tarkov_path.py)
 - Event-driven system (src/tarkov_tool/event_manger.py; src/tarkov_tool/events.py)

# Project Structure
```
TarkovTool/
├── src/
│   ├── tarkov_tool/                    # Main library
│   │   ├── config.py                   # Configuration
│   │   ├── constants.py                # Constants
│   │   ├── event_manger.py             # Event manager
│   │   ├── events.py                   # Event definitions
│   │   ├── reference_data.py           # Reference data
│   │   ├── tarkov_time.py              # Tarkov time calculation
│   │   ├── watcher.py                  # Log watcher
│   │   ├── tarkov/                     # Tarkov game interaction
│   │   │   ├── config.py               # Game config
│   │   │   ├── datamodel.py            # Data model
│   │   │   ├── is_runing.py            # Game running detection
│   │   │   ├── locales.py              # Locales
│   │   │   ├── log.py                  # Log parsing
│   │   │   ├── message.py              # Game messages
│   │   │   ├── path.py                 # Game paths
│   │   │   ├── screenshot.py           # Screenshot processing
│   │   │   ├── setting.py              # Game settings
│   │   │   ├── status.py               # Game status
│   │   │   ├── localization/           # Localization resources
│   │   │   └── locations/              # Map data
│   │   ├── tarkovapi/                  # Tarkov API client
│   │   └── util/                       # Utility modules
│   │       ├── log_archive.py          # Log archiving
│   │       └── ...
│   └── tarkov_tool_util/
│       └── tarkovdev/                  # tarkov.dev utility
├── tests/                              # Tests
├── scripts/                            # Scripts
├── doc/                                # Documentation
├── notes/                              # Development notes
├── prompts/                            # AI prompts
├── reference/                          # Reference projects (GitHub clones)
│   ├── carlsmei_tarkovdata/
│   ├── EFT-CaseCompilator-Screenshot-Cropper-Combinator/
│   ├── eft-where-am-i/
│   ├── RatEye/
│   ├── RatScanner/
│   ├── RatStash/
│   ├── tarkov-api/
│   ├── tarkov-dev/
│   ├── tarkov-dev-svg-maps/
│   ├── tarkov-market-helper/
│   ├── tarkov-tilty-frontend-opensource/
│   ├── TarkovMapTracker/
│   ├── TarkovMonitor/
│   ├── TarkovTracker_tarkovdata/
│   ├── tilda-eft/
│   └── Z_repo_doc/
└── util/                               # Utilities
```

# Data
## Tarkov Sensitive Data
This project hashes any Tarkov sensitive data it reads by default to protect privacy.
This behavior is controlled by the class attribute `tarkov_tool.config.Config.enable_sensitive_data_hashing_for_tarkov`.

Tarkov sensitive data includes but is not limited to:
 - AccountID
 - ProFileID

>[!NOTE]
>This is designed to hash the data upon reading and parsing before output.

# Terminology
|Term|Description|Notes|
|-|-|-|
|Game Session|Refers to a complete lifecycle of a game process. From process start to termination counts as one Session||
|Raid|Refers to a battle session within the game. Typically the process from a player entering a map, completing tasks or combat, to extraction|Even if the raid_id differs after transferring to another map, it is still considered the same raid (based on the game's quest criteria for the same raid)|
|Raid Session|Refers to a component of a Raid, describing "different segments of the same raid"|Due to situations like disconnection and reconnection, map transfers, etc., the same Raid may be split into multiple Sessions|
|Raid Group|Refers to the members of a squad who entered the same raid together|Due to server issues, actual members may differ from those recorded in logs|

> Based on existing observations, the terms above have the following relationships:
>
> A Raid consists of one or more Raid Sessions
>
> Generally, a Raid has only one corresponding Raid Group; if there is a map transfer, there may be different Raid Groups
>
> The same Raid may span different Game Sessions, for example due to the player restarting the game or an unexpected game exit

# Data Differences
The developer used a PVE Profile created before game version 1.0 to play and obtain logs for developing this project.
Therefore, there may be differences from logs generated by PVE Profiles created after version 1.0.

For details on the referenced log files and their corresponding game versions, please see [notes\used_tarkov_log_versions.txt](notes\used_tarkov_log_versions.txt)

# References
[Escape from Tarkov [Sound Effects]](https://www.youtube.com/playlist?list=PLq44zq7R2Kq7mUiGSXXjkcjHR7EDzHo6L)
[Escape from Tarkov Wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki)
[Tarkov GraphQL API](https://api.tarkov.dev/)
## ID
[tarkynator.com](https://tarkynator.com/common-id)
[sp-tarkov/server](https://github.com/sp-tarkov/server/blob/96e5b73f0f00d0e0a75d83f216bcde0dec387605/project/assets/database/traders/54cb50c76803fa8b248b4571/dialogue.json#L4)

## Copyright Notice
### MindEscape Font
```
assets/font/MindEscape.ttf
```
A font similar to the Tarkov Time font

From [onlinewebfonts](http://www.onlinewebfonts.com)

Website copyright requirements
```html
<div>Fonts made from <a href="http://www.onlinewebfonts.com">Web Fonts</a> is licensed by CC BY 4.0</div>
```

>[!IMPORTANT]
>This project automatically downloads files from other GitHub projects at runtime. Please comply with their respective license terms when using them.

# License
Copyright (c) 2026 SvCpu
This project is licensed under the GNU LGPL v3 - see the [LICENSE](./License) file for details.

> [!CAUTION]
>This project is not affiliated with BSG/Battlestate Games
>
>The developer assumes no responsibility for any in-game penalties, bans, or other consequences arising from the use of this tool library
>
>Although based on the operating principles of this tool library, no such consequences should occur
>
>Use at your own risk


[escape-from-tarkov]: https://www.escapefromtarkov.com/
