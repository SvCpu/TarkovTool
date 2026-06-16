# language in log
only game start will log select language one time
in game change lang will not log

# log file chage

log file name add `_000` start with `1.0.0.0.41760`

the last log can find with after 1.0 is `log_2025.11.12_13-04-18_0.16.9.5.40743`

so log parse need has beta release two version

## log timezone
### before `1.0.0.0.41787`
 - the time has not time zone in log
 - the time in log is not utc time , is system time zone, need standardization

# used log
## beta
field:
```
Session mode: 
SelectProfile ProfileId:
Got notification | GroupMatchInviteAccept
Got notification | GroupMatchInviteSend
Got notification | GroupMatchUserLeave
Got notification | GroupMatchWasRemoved
Got notification | GroupMatchRaidSettings
Got notification | GroupMatchRaidReady
application|Matching with group id
application|LocationLoaded
application|MatchingCompleted
application|TRACE-NetworkGameCreate profileStatus
application|GameStarting
application|GameStarted
application|Network game matching aborted
application|Network game matching cancelled
Got notification | UserMatchOver
application|Init: pstrGameVersion: 
Got notification | ChatMessageReceived
Error|Default|[Transit] Flag:Common
application|scene preset path:maps
```

file:
```
application
errors
notifications
```

## release
field(add from beta):
```
SelectedProfile ProfileId:
Control settings:
```

file:
```
application
push-notifications
```