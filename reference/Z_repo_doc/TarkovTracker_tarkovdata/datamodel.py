from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ─── amunition.json ────────────────────────────────────────────────


class Ballistics(BaseModel):
    damage: int
    armorDamage: int
    fragmentationChance: float
    ricochetChance: float
    penetrationChance: float
    penetrationPower: int
    accuracy: int
    recoil: int
    initialSpeed: int


class Ammo(BaseModel):
    id: str
    name: str
    shortName: str
    weight: float
    caliber: str
    stackMaxSize: int
    tracer: bool
    tracerColor: str
    ammoType: str
    projectileCount: int
    ballistics: Ballistics


# 結構: Dict[str, Ammo] 以 ammo id 為鍵


# ─── hideout.json ──────────────────────────────────────────────────


class StationLocale(BaseModel):
    en: str
    ru: Optional[str] = None


class Station(BaseModel):
    id: int
    locales: StationLocale
    function: str
    imgSource: str
    disabled: Optional[bool] = None


class Requirement(BaseModel):
    type: str  # "module" | "item" | "trader" | "skill"
    name: Any  # str (module/item/skill) or int (trader id)
    quantity: int
    id: int


class HideoutModule(BaseModel):
    module: str
    level: int
    require: List[Requirement]
    id: int
    stationId: int


class HideoutData(BaseModel):
    stations: List[Station]
    modules: List[HideoutModule]


# ─── item_presets.json ──────────────────────────────────────────────


class Part(BaseModel):
    id: str
    quantity: int


class ItemPreset(BaseModel):
    id: str
    name: str
    appendName: str
    default: bool
    baseId: str
    parts: List[Part]


# 結構: Dict[str, ItemPreset] 以 preset id 為鍵


# ─── items.en.json ─────────────────────────────────────────────────


class ItemName(BaseModel):
    id: str
    name: str
    shortName: str


# 結構: Dict[str, ItemName] 以 item id 為鍵


# ─── levels.json ───────────────────────────────────────────────────


class Level(BaseModel):
    exp: int
    group: str


# 結構: Dict[str, Level] 以等級字串 "1".."75" 為鍵


# ─── maps.json ─────────────────────────────────────────────────────


class MapLocale(BaseModel):
    en: str
    ru: Optional[str] = None


class RaidDuration(BaseModel):
    day: int
    night: int


class SvgInfo(BaseModel):
    file: str
    floors: List[str]
    defaultFloor: str
    coordinateRotation: int
    bounds: List[List[float]]


class GameMap(BaseModel):
    id: int
    tdevId: str
    locale: MapLocale
    wiki: str
    description: Optional[str] = None
    enemies: Optional[List[str]] = None
    raidDuration: Optional[RaidDuration] = None
    svg: SvgInfo


# 結構: Dict[str, GameMap] 以地圖名稱 (factory, customs...) 為鍵


# ─── objective_gps.json ────────────────────────────────────────────


class ObjectiveGPS(BaseModel):
    map: str
    leftPercent: float
    topPercent: float
    floor: str


# 結構: Dict[str, ObjectiveGPS] 以 objective id 為鍵


# ─── objective_maps.json ───────────────────────────────────────────

# 結構: Dict[str, List[str]] objective_id -> [map_tdev_id, ...]


# ─── quests.json ────────────────────────────────────────────────────


class QuestRequirement(BaseModel):
    level: int
    quests: List[int]


class Reputation(BaseModel):
    trader: int
    rep: float


class WithCondition(BaseModel):
    type: str  # "stat" | "attachment" | "cells" | "part" | ...
    name: Optional[str] = None
    value: Optional[Any] = None


class GPSPosition(BaseModel):
    leftPercent: float
    topPercent: float
    floor: str


class Objective(BaseModel):
    type: str  # "kill" | "collect" | "find" | "key" | "mark" | "pickup" | "place" | "build" | "locate" | "reputation" | "skill" | "warning"
    target: str  # item id or name
    number: int
    location: int  # map id, -1 = any
    id: int
    tool: Optional[str] = None
    hint: Optional[str] = None
    gps: Optional[GPSPosition] = None
    have: Optional[int] = None  # 0 or 1 (boolean flag)
    with_: Optional[List[Any]] = Field(None, alias="with")
    # with_ 可以是 List[str] (簡單條件) 或 List[WithCondition] (結構化條件)


class Quest(BaseModel):
    id: int
    require: QuestRequirement
    giver: int
    turnin: int
    title: str
    locales: Dict[str, str]
    wiki: str
    exp: int
    unlocks: Optional[List[str]] = None
    reputation: List[Reputation]
    reputationFailure: Optional[List[Reputation]] = None
    objectives: List[Objective]
    gameId: str
    alternatives: Optional[List[int]] = None
    deprecated: Optional[bool] = None
    nokappa: Optional[bool] = None


# 結構: List[Quest]


# ─── task_alternatives.json ─────────────────────────────────────────

# 結構: Dict[str, List[str]] quest_gameId -> [alternative_gameId, ...]


# ─── traders.json ──────────────────────────────────────────────────


class LoyaltyLevel(BaseModel):
    level: int
    requiredLevel: int
    requiredReputation: float
    requiredSales: int


class TraderLocale(BaseModel):
    en: str
    ru: Optional[str] = None


class Trader(BaseModel):
    id: int
    name: str
    locale: TraderLocale
    wiki: str
    description: str
    currencies: List[str]
    salesCurrency: str
    loyalty: List[LoyaltyLevel]


# 結構: Dict[str, Trader] 以 trader key (prapor, therapist...) 為鍵
