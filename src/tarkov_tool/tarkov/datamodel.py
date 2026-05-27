from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
from typing import Callable, Optional, Final
from pydantic import BaseModel, Field

datetimeformatstr:Final[str] = r'%Y-%m-%d %H:%M:%S.%f %z'
datetimetostr:Callable[[datetime],str] = lambda x: x.strftime(datetimeformatstr)
strtodatetime:Callable[[str],datetime] = lambda x: datetime.strptime(x, datetimeformatstr)

parse_strings:Final[list[str]] = [
'Session mode: ',
'SelectProfile ProfileId:',
'Got notification | GroupMatchInviteAccept',
'Got notification | GroupMatchInviteSend',
'Got notification | GroupMatchUserLeave',
'Got notification | GroupMatchWasRemoved',
'Got notification | GroupMatchRaidSettings',
'Got notification | GroupMatchRaidReady',
'application|Matching with group id',
'application|LocationLoaded',
'application|MatchingCompleted',
'application|TRACE-NetworkGameCreate profileStatus',
'application|GameStarting',
'application|GameStarted',
'application|Network game matching aborted',
'application|Network game matching cancelled',
'Got notification | UserMatchOver',
'application|Init: pstrGameVersion: ',
'Got notification | ChatMessageReceived',
'Error|Default|[Transit] Flag:Common',
'application|scene preset path:maps',
]

map_bundles:Final[dict[str,str]] = {
    "city_preset": "TarkovStreets",
    "customs_preset": "bigmap",
    "factory_day_preset": "factory4_day",
    "factory_night_preset": "factory4_night",
    "laboratory_preset": "laboratory",
    "labyrinth_preset": "Labyrinth",
    "lighthouse_preset": "Lighthouse",
    "rezerv_base_preset": "RezervBase",
    "sandbox_preset": "Sandbox",
    "sandbox_high_preset": "Sandbox_high",
    "shopping_mall": "Interchange",
    "shoreline_preset": "Shoreline",
    "woods_preset": "Woods",
}

class MessageType(Enum):
    PlayerMessage = 1
    Insurance = 2
    FleaMarket = 4
    InsuranceReturn = 8
    TaskStarted = 10
    TaskFailed = 11
    TaskFinished = 12
    TwitchDrop = 13
    @classmethod
    def from_value(cls, value: int) -> Optional["MessageType"]:
        return cls._value2member_map_.get(value)

class TaskStatus(Enum):
    none = 0
    started = 10
    failed = 11
    finished = 12

class GameLogType(Enum):
    Application = 'application'
    Notifications = 'notifications'
    Traces = 'traces'
    Errors = 'errors'
    Unknow = 'unknow'

class Location(Enum):
    Lighthouse = 'Lighthouse'
    TarkovStreets = 'TarkovStreets'
    Shoreline = 'Shoreline'
    Reserve = 'RezervBase'
    GroundZero_High = 'Sandbox_high'
    GroundZero = 'Sandbox'
    FactoryDay = 'factory4_day'
    Woods = 'Woods'
    Interchange = 'Interchange'
    Labs = 'laboratory'
    Customs = 'bigmap'

@dataclass
class Kill:
    kill_from: str
    Faction: str
    kill_time: int

@dataclass
class KillList:
    Killer: str
    EliminatedTagets: list[Kill]

class ProfileType(Enum):
    PVE = "Pve"
    Regular = "Regular"

class ProfileSide(Enum):
    USEC = 'Usec'
    BEAR = 'Bear'
    Unknown = "Unknown"

class RaidType(Enum):
    PVE = "PVE"
    Local = 'Local'
    '本地戰局'
    Local_Halted = 'local_halted'
    '未完成的本地戰局'
    Unknown = "Unknown"
    PMC = "PMC"
    Scav = "Scav"

class GamePurchaseVersion(Enum):
    Standard = 'standard'
    EdgeOfDarkness = 'edge_of_darkness'
    EodTueEdition = 'eod_tue_edition'
    UnheardEdition = 'unheard_edition'

@dataclass
class LogFolderInfo:
    path: str|Path
    timestamp: datetime
    version: str
    @property
    def info_hash(self)->str:
        return hashlib.blake2s(f'{self.timestamp} From {self.version}'.encode("utf-8"), digest_size=4).hexdigest()

class LogVersion(Enum):
    'game version > 1.0 = release'
    Beta = 'beta'
    Release = 'release'

class Profile(BaseModel):
    type: ProfileType = Field(default=ProfileType.Regular)
    id: str
    

class Player(BaseModel):
    ac_id: str = Field(default=None)
    pve_profile_id: str = Field(default=None)
    regular_profile_id: str = Field(default=None)
    nickname: str = Field(default=None)
    side:ProfileSide = Field(default=ProfileSide.Unknown)
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls,)

class Position(BaseModel):
    x: float
    y: float
    z: float

class ScreenshotInfo(BaseModel):
    filename: str|Path
    position: Position
    yaw: float
    pitch: float