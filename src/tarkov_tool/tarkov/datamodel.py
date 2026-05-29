from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Final, Iterable
from pydantic import BaseModel, Field

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
    "icebreaker":"Icebreaker",
}

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
    Icebreaker = 'Icebreaker'

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

class LogFolder(BaseModel):
    path: Path
    timestamp: datetime
    version: str

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
    start_time: datetime
    started_time: datetime = Field(default=None)
    'Deprecated in tarkov 1.0'
    end_time: datetime

class Raid(BaseModel):
    id: str
    short_id: Optional[str] = Field(default=None)
    type: RaidType = Field(default=RaidType.Unknown)
    profile_type: ProfileType = Field(default=ProfileType.Regular)
    location: Optional[Location] = Field(default=None)
    local: bool = Field(default=False)
    start_time: datetime
    end_time: datetime
    in_raid_time: int
    sessions:list[RaidSession] = Field(default_factory=list)

class Position(BaseModel):
    x: float
    y: float
    z: float

class ScreenshotInfo(BaseModel):
    filename: str
    position: Position
    yaw: float
    pitch: float