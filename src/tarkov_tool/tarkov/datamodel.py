from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Final, Iterable

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import core_schema

class Location(Enum):
    Lighthouse = 'Lighthouse'
    TarkovStreets = 'TarkovStreets'
    Shoreline = 'Shoreline'
    Reserve = 'Reserve'
    GroundZero_High = 'GroundZero_High'
    GroundZero = 'GroundZero'
    FactoryDay = 'FactoryDay'
    Woods = 'Woods'
    Interchange = 'Interchange'
    Labs = 'Labs'
    Customs = 'Customs'
    Icebreaker = 'Icebreaker'
    Terminal = 'Terminal'

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

@dataclass
class Kill:
    kill_from: str
    Faction: str
    kill_time: int

@dataclass
class KillList:
    Killer: str
    EliminatedTagets: list[Kill]

class Version:
    __slots__ = ('_raw_version', '_major', '_minor', '_patch', '_subpatch', '_build')

    def __init__(self, version: str):
        self._raw_version = version
        parts = version.split(".")
        if len(parts) != 5:
            raise ValueError
        self._major = int(parts[0])
        self._minor = int(parts[1])
        self._patch = int(parts[2])
        self._subpatch = int(parts[3])
        self._build = int(parts[4])

    @property
    def major(self): return self._major
    @property
    def minor(self): return self._minor
    @property
    def patch(self): return self._patch
    @property
    def subpatch(self): return self._subpatch
    @property
    def build(self): return self._build
    def __repr__(self):
        return (f"<GameVersion {self.major}.{self.minor}.{self.patch}."
                f"{self.subpatch}.{self.build}>")
    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}.{self.subpatch}.{self.build}"
    def __lt__(self, other:'Version'):
        return (self.major, self.minor, self.patch, self.subpatch, self.build) < \
               (other.major, other.minor, other.patch, other.subpatch, other.build)
    def __eq__(self, other:'Version'):
        return (self.major, self.minor, self.patch, self.subpatch, self.build) == \
               (other.major, other.minor, other.patch, other.subpatch, other.build)
    def __gt__(self, other:'Version'):
        return (self.major, self.minor, self.patch, self.subpatch, self.build) > \
               (other.major, other.minor, other.patch, other.subpatch, other.build)
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: str(v),
                return_schema=core_schema.str_schema()
            )
        )
    @classmethod
    def _validate(cls, value):
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            return cls(value)
        raise TypeError("必须是 Version 或字符串")

class LogFolder(BaseModel):
    path: Path
    timestamp: datetime
    version: Version
    log_file_count:int = Field(default=0)
    model_config = ConfigDict(
        validate_assignment=True,
        json_encoders={Path: str, Version: str}
    )

class LogParserDataSource(BaseModel):
    logfolders:list[LogFolder] = Field(default=None)
    log_file_count:int = Field(default=0)

class LogVersion(Enum):
    'game version > 1.0 = release'
    Beta = 'beta'
    Release = 'release'

class ProfileType(Enum):
    PVE = "Pve "
    Regular = "Regular"

class ProfileSide(Enum):
    USEC = 'Usec'
    BEAR = 'Bear'
    Unknown = "Unknown"

class RaidType(Enum):
    PMC = 'pmc'
    Scav = 'scav'
    Unknown = "unknown"

class RaidStatus(Enum):
    Incomplete = 'incomplete'
    '未完成戰局'
    Done = 'done'
    '完成戰局'
    Invalid = 'invalid'
    '失效戰局(裝備重置)'

class GamePurchaseVersion(Enum):
    Standard = 'standard'
    EdgeOfDarkness = 'edge_of_darkness'
    EodTueEdition = 'eod_tue_edition'
    UnheardEdition = 'unheard_edition'

class Profile(BaseModel):
    id: str
    type: ProfileType = Field(default=ProfileType.Regular)
    level: int = Field(default=0)

class PlayerHealth(BaseModel):
    pass

class Player(BaseModel):
    ac_id: int = Field(default=None)
    pve_profile_id: str = Field(default=None)
    regular_profile_id: str = Field(default=None)
    game_purchase_version: Optional[GamePurchaseVersion] = Field(default=GamePurchaseVersion.Standard)
    nickname: str = Field(default=None)
    side:ProfileSide = Field(default=None)
    level: int = Field(default=None)
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls,)
    def is_same_player(self, other)->bool:
        if not isinstance(other, Player):
            raise TypeError
        if self.ac_id == other.ac_id:
            return True
        if self.nickname == other.nickname and (self.ac_id is None or other.ac_id is None):
            return True
        return False
    def is_player_in(self, others:Iterable['Player'])->bool:
        for m in others:
            if m.is_same_player(self):
                return True
        return False

class RaidGroup(BaseModel):
    id: str = Field(default=None)
    leader:Player = Field(default=None)
    members:list[Player] = Field(default_factory=list)
    max_member: int
    def join(self, member:Player):
        if len(self.members) < self.max_member and all(not m.is_same_player(member) for m in self.members):
            self.members.append(member)
    def leave(self, member:Player):
        if member.is_player_in(self.members):
            for m in self.members:
                if m.is_same_player(member):
                    self.members.remove(m)
                    break

class RaidSession(BaseModel):
    start_time: datetime = Field(default=None)
    started_time: datetime = Field(default=None)
    'Deprecated in tarkov 1.0'
    end_time: datetime = Field(default=None)

class Raid(BaseModel):
    id: str
    short_id: Optional[str] = Field(default=None)
    type: RaidType = Field(default=RaidType.Unknown)
    profile_type: ProfileType = Field(default=ProfileType.Regular)
    location: Optional[Location] = Field(default=None)
    local: bool = Field(default=False)
    start_time: datetime = Field(default=None)
    end_time: datetime = Field(default=None)
    in_raid_time: int = Field(default=None)
    sessions:list[RaidSession] = Field(default_factory=list)

class Position(BaseModel):
    x: float
    y: float
    z: float

class ScreenshotInfo(BaseModel):
    filepath: Path
    filename: str
    position: Position|None = Field(default=None)
    yaw: float|None = Field(default=None)
    pitch: float|None = Field(default=None)
    model_config = ConfigDict(
        validate_assignment=True,
        json_encoders={Path: str}
    )