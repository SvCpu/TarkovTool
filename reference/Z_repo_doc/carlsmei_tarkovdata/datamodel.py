from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# items.json
# ============================================================

class Prefab(BaseModel):
    path: str = ""
    rcid: str = ""


class ItemProps(BaseModel):
    Name: str = ""
    ShortName: str = ""
    Description: str = ""
    Weight: float = 0
    Width: int = 1
    Height: int = 1
    StackMaxSize: int = 1
    BackgroundColor: str = ""
    ItemSound: str = ""
    Prefab: Prefab = Field(default_factory=Prefab)
    UsePrefab: Prefab = Field(default_factory=Prefab)
    LootExperience: int = 0
    ExamineExperience: int = 0
    ExaminedByDefault: bool = False
    StackObjectsCount: int = 1
    HideEntrails: bool = False
    RepairCost: int = 0
    RepairSpeed: int = 0
    MergesWithChildren: bool = False
    CanSellOnRagfair: bool = True
    ConflictingItems: List[str] = Field(default_factory=list)
    Unlootable: bool = False
    UnlootableFromSlot: str = ""
    UnlootableFromSide: List[str] = Field(default_factory=list)
    RagFairCommissionModifier: float = 1.0
    QuestItem: bool = False
    QuestStashMaxCount: int = 0
    AnimationVariantsNumber: int = 0


class ItemEntry(BaseModel):
    _id: str = Field(alias="_id")
    _name: str = Field(alias="_name")
    _parent: str = Field(alias="_parent")
    _type: str = Field(alias="_type")  # "Node" | "Item"
    _props: ItemProps = Field(alias="_props")
    _proto: Optional[str] = Field(default=None, alias="_proto")


# ============================================================
# items-prices.json
# ============================================================

ItemsPrices = Dict[str, int]


# ============================================================
# customization.json
# ============================================================

class AssetPath(BaseModel):
    path: str = ""
    rcid: str = ""


class CustomizationProps(BaseModel):
    Name: str = ""
    ShortName: str = ""
    Description: str = ""
    AvailableAsDefault: bool = False
    Side: List[str] = Field(default_factory=list)
    Prefab: Optional[Prefab] = None
    WatchPosition: Optional[Dict[str, float]] = None
    BodyPart: Optional[str] = None
    IntegratedArmorVest: Optional[bool] = None
    Feet: Optional[str] = None
    ProfileVersions: List[Any] = Field(default_factory=list)
    Game: List[Any] = Field(default_factory=list)
    Interaction: Optional[str] = None
    AssetPath: Optional[AssetPath] = None


class CustomizationEntry(BaseModel):
    _id: str = Field(alias="_id")
    _name: str = Field(alias="_name")
    _parent: str = Field(alias="_parent")
    _type: str = Field(alias="_type")
    _props: CustomizationProps = Field(alias="_props")


# ============================================================
# locations.json
# ============================================================

class Vector3(BaseModel):
    x: float = 0
    y: float = 0
    z: float = 0


class NonWaveGroupScenario(BaseModel):
    MinToBeGroup: int = 0
    MaxToBeGroup: int = 0


class Location(BaseModel):
    AccessKeys: List[str] = Field(default_factory=list)
    AccessKeysPvE: List[str] = Field(default_factory=list)
    Area: int = 0
    AveragePlayTime: int = 0
    AveragePlayerLevel: int = 0
    BotAssault: int = 0
    BotEasy: int = 0
    BotHard: int = 0
    BotImpossible: int = 0
    BotMarksman: int = 0
    BotMax: int = 0
    BotMaxPvE: int = 0
    BotNormal: int = 0
    BotSpawnCountStep: int = 0
    BotSpawnPeriodCheck: int = 0
    BotSpawnTimeOffMax: int = 0
    BotSpawnTimeOffMin: int = 0
    BotSpawnTimeOnMax: int = 0
    BotSpawnTimeOnMin: int = 0
    BotStart: int = 0
    BotStartPlayer: int = 0
    BotStop: int = 0
    DisabledScavExits: str = ""
    EnableCoop: bool = False
    Enabled: bool = False
    EscapeTimeLimit: int = 0
    EscapeTimeLimitCoop: int = 0
    ForceOfflineRaidInPVE: bool = False
    ForceOnlineRaidInPVE: bool = False
    GlobalContainerChanceModifier: float = 1.0
    HeatmapCellSize: Vector3 = Field(default_factory=Vector3)
    HeatmapLayers: List[str] = Field(default_factory=list)
    IconX: int = 0
    IconY: int = 0
    IsSecret: bool = False
    Locked: bool = False
    LockedByQuest: bool = False
    MaxBotPerZone: int = 0
    MaxCoopGroup: int = 0
    MaxDistToFreePoint: int = 0
    MaxPlayers: int = 0
    MinDistToFreePoint: int = 0
    MinPlayerLvlAccessKeys: int = 0
    MinPlayers: int = 0
    Name: str = ""
    NewSpawn: bool = False
    NewSpawnForPlayers: bool = False
    NonWaveGroupScenario: Optional[NonWaveGroupScenario] = None
    OldSpawn: bool = False
    OpenZones: str = ""
    PlayersIds: List[str] = Field(default_factory=list)
    RevelationMode: bool = False
    SavageLeftChance: int = 0
    SavagePlayCooldown: int = 0
    SavagePlayCooldownPvE: int = 0
    SeasonsRange: List[Any] = Field(default_factory=list)
    ShutDelay: int = 0
    SpawnPoint: str = ""
    SpawnAreas: List[Any] = Field(default_factory=list)


class LocationsWrapper(BaseModel):
    locations: Dict[str, Location]


# ============================================================
# globals.json
# ============================================================

GlobalsConfig = Dict[str, Any]


class GlobalsWrapper(BaseModel):
    config: GlobalsConfig


# ============================================================
# distrib.json
# ============================================================

class Distrib(BaseModel):
    version: str = ""
    hash: str = ""
    downloadUri: str = ""
    requiredFreeSpace: int = 0
    unpackedUri: str = ""
    torrentUri: str = ""


# ============================================================
# ending.json / prestige.json / achievements/list.json
# ============================================================

class IllustrationConfig(BaseModel):
    image: Optional[str] = None
    bigImage: Optional[str] = None
    isBigImage: bool = False


class Reward(BaseModel):
    unknown: bool = False
    gameMode: List[str] = Field(default_factory=list)
    availableInGameEditions: List[str] = Field(default_factory=list)
    illustrationConfig: Optional[IllustrationConfig] = None
    isHidden: bool = False
    isImportant: bool = False
    id: str = ""
    target: str = ""
    type: str = ""


class ConditionProps(BaseModel):
    index: int = 0
    dynamicLocale: bool = False
    visibilityConditions: List[Any] = Field(default_factory=list)
    globalQuestCounterId: str = ""
    parentId: str = ""
    entryPoint: Optional[str] = None
    dialogId: Optional[str] = None
    fromTraderId: Optional[str] = None


class Counter(BaseModel):
    id: str = ""
    conditions: List[Any] = Field(default_factory=list)


class Condition(BaseModel):
    index: int = 0
    dynamicLocale: bool = False
    visibilityConditions: List[Any] = Field(default_factory=list)
    globalQuestCounterId: str = ""
    parentId: str = ""
    dialogId: Optional[str] = None
    entryPoint: Optional[str] = None
    fromTraderId: Optional[str] = None
    id: str = ""
    props: ConditionProps = Field(default_factory=ConditionProps)
    questNoteId: Optional[str] = None
    value: Any = None
    compareMethod: Optional[str] = None
    conditionType: str = ""
    target: Optional[str] = None
    status: Optional[List[int]] = None
    availableAfter: int = 0
    dispersion: int = 0
    isFinisher: bool = False
    counter: Optional[Counter] = None
    oneSessionOnly: Optional[bool] = None
    completeInSeconds: int = 0
    doNotResetIfCounterCompleted: Optional[bool] = None
    isResetOnConditionFailed: Optional[bool] = None
    isNecessary: Optional[bool] = None


class Element(BaseModel):
    id: str = ""
    imageUrl: Optional[str] = None
    assetPath: Optional[str] = None
    systemName: Optional[str] = None
    rewards: List[Reward] = Field(default_factory=list)
    conditions: Optional[Dict[str, List[Condition]]] = None
    items: Optional[List[Any]] = None


class ElementsWrapper(BaseModel):
    elements: List[Element]


# ============================================================
# achievements/statistic.json
# ============================================================

AchievementStatistics = Dict[str, float]


# ============================================================
# tapes.json / subtitle-track.json
# ============================================================

class SubtitleSegment(BaseModel):
    id: str = ""
    start: float = 0
    end: float = 0


class Tape(BaseModel):
    id: str = ""
    subtitles: List[SubtitleSegment] = Field(default_factory=list)


class SubtitleTrack(BaseModel):
    id: str = ""
    subtitles: List[SubtitleSegment] = Field(default_factory=list)


# ============================================================
# hideout/areas.json
# ============================================================

class Requirement(BaseModel):
    type: str = ""
    areaType: Optional[int] = None
    requiredLevel: Optional[int] = None
    templateId: Optional[str] = None
    count: Optional[int] = None
    isFunctional: Optional[bool] = None
    isEncoded: Optional[bool] = None
    isSpawnedInSession: Optional[bool] = None
    questId: Optional[str] = None


class Bonus(BaseModel):
    pass


class Improvement(BaseModel):
    pass


class Stage(BaseModel):
    requirements: List[Requirement] = Field(default_factory=list)
    bonuses: List[Bonus] = Field(default_factory=list)
    slots: int = 0
    constructionTime: float = 0
    description: str = ""
    container: str = ""
    autoUpgrade: bool = False
    displayInterface: bool = False
    improvements: List[Improvement] = Field(default_factory=list)
    globalCounterId: Optional[str] = None


class HideoutArea(BaseModel):
    _id: str = ""
    type: int = 0
    enabled: bool = False
    needsFuel: bool = False
    takeFromSlotLocked: bool = False
    craftGivesExp: bool = False
    displayLevel: bool = False
    requirements: List[Requirement] = Field(default_factory=list)
    stages: Dict[str, Stage] = Field(default_factory=dict)
    enableAreaRequirements: bool = False
    parentArea: str = ""


# ============================================================
# hideout/recipes.json
# ============================================================

class RecipeRequirement(BaseModel):
    templateId: Optional[str] = None
    count: Optional[int] = None
    isFunctional: bool = False
    isEncoded: bool = False
    isSpawnedInSession: bool = False
    type: str = ""
    areaType: Optional[int] = None
    requiredLevel: Optional[int] = None


class Recipe(BaseModel):
    _id: str = ""
    areaType: int = 0
    requirements: List[RecipeRequirement] = Field(default_factory=list)
    productionTime: float = 0
    needFuelForAllProductionTime: bool = False
    locked: bool = False
    endProduct: str = ""
    continuous: bool = False
    count: int = 0
    productionLimitCount: int = 0
    isEncoded: bool = False
    isCodeProduction: bool = False


class RecipesWrapper(BaseModel):
    recipes: List[Recipe]


# ============================================================
# hideout/settings.json
# ============================================================

class HideoutSettings(BaseModel):
    generatorSpeedWithoutFuel: float = 0
    generatorFuelFlowRate: float = 0
    airFilterUnitFlowRate: float = 0
    gpuBoostRate: float = 0
    cultistAmuletBonusPercent: float = 0


# ============================================================
# hideout/qte.json
# ============================================================

class QtePosition(BaseModel):
    x: float = 0
    y: float = 0


class QteSuccessRange(BaseModel):
    x: float = 0
    y: float = 0


class QuickTimeEvent(BaseModel):
    type: str = ""
    position: QtePosition = Field(default_factory=QtePosition)
    speed: float = 0
    successRange: QteSuccessRange = Field(default_factory=QteSuccessRange)
    key: str = ""
    startDelay: float = 0
    endDelay: float = 0


class QTE(BaseModel):
    id: str = ""
    area: int = 0
    areaLevel: int = 0
    quickTimeEvents: List[QuickTimeEvent] = Field(default_factory=list)


# ============================================================
# hideout/customization.json
# ============================================================

class HideoutCustomizationCondition(BaseModel):
    index: int = 0
    dynamicLocale: bool = False
    visibilityConditions: List[Any] = Field(default_factory=list)
    globalQuestCounterId: str = ""
    parentId: str = ""
    dialogId: Optional[str] = None
    entryPoint: Optional[str] = None
    fromTraderId: Optional[str] = None
    id: str = ""
    props: ConditionProps = Field(default_factory=ConditionProps)
    questNoteId: Optional[str] = None
    conditionType: str = ""


class HideoutCustomization(BaseModel):
    id: str = ""
    conditions: List[HideoutCustomizationCondition] = Field(default_factory=list)
    type: str = ""
    index: int = 0
    systemName: str = ""
    isEnabled: bool = False
    itemId: str = ""


class HideoutCustomizationWrapper(BaseModel):
    globals: List[HideoutCustomization]


# ============================================================
# trading/settings.json
# ============================================================

class RepairInfo(BaseModel):
    availability: bool = False
    quality: str = ""
    excluded_id_list: List[str] = Field(default_factory=list)
    excluded_category: List[str] = Field(default_factory=list)
    currency: str = ""
    currency_coefficient: int = 0


class InsuranceInfo(BaseModel):
    availability: bool = False
    min_payment: int = 0
    min_return_hour: int = 0
    max_return_hour: int = 0
    max_storage_time: int = 0
    excluded_category: List[str] = Field(default_factory=list)


class LoyaltyLevel(BaseModel):
    minLevel: int = 0
    minSalesSum: int = 0
    minStanding: float = 0
    buy_price_coef: int = 0
    repair_price_coef: int = 0
    insurance_price_coef: str = ""
    exchange_price_coef: int = 0
    heal_price_coef: int = 0


class Trader(BaseModel):
    _id: str = ""
    customization_seller: bool = False
    name: str = ""
    surname: str = ""
    nickname: str = ""
    location: str = ""
    avatar: str = ""
    balance_rub: int = 0
    balance_dol: int = 0
    balance_eur: int = 0
    unlockedByDefault: bool = False
    discount: str = ""
    discount_end: int = 0
    buyer_up: bool = False
    currency: str = ""
    nextResupply: int = 0
    repair: RepairInfo = Field(default_factory=RepairInfo)
    insurance: InsuranceInfo = Field(default_factory=InsuranceInfo)
    medic: bool = False
    gridHeight: int = 0
    availableInRaid: bool = False
    sell_modifier_for_prohibited_items: int = 0
    loyaltyLevels: List[LoyaltyLevel] = Field(default_factory=list)


# ============================================================
# trading/customization/offers-{bear,usec}.json
# ============================================================

class ItemRequirement(BaseModel):
    id: Optional[str] = None
    count: int = 0
    _tpl: str = ""
    onlyFunctional: bool = False
    type: str = ""


class OfferRequirements(BaseModel):
    loyaltyLevel: int = 0
    profileLevel: int = 0
    standing: int = 0
    skillRequirements: List[Any] = Field(default_factory=list)
    questRequirements: List[str] = Field(default_factory=list)
    achievementRequirements: List[str] = Field(default_factory=list)
    itemRequirements: List[ItemRequirement] = Field(default_factory=list)
    requiredTid: str = ""
    prestigeLevel: int = 0


class CustomizationOffer(BaseModel):
    _id: str = ""
    tid: str = ""
    suiteId: str = ""
    isActive: bool = False
    isHiddenInPVE: bool = False
    externalObtain: bool = False
    internalObtain: bool = False
    requirements: OfferRequirements = Field(default_factory=OfferRequirements)


# ============================================================
# trading/customization/storage.json
# ============================================================

class CustomizationStorage(BaseModel):
    id: str = ""
    source: str = ""
    type: str = ""


# ============================================================
# dialogue/list.json
# ============================================================

class DialogueMedia(BaseModel):
    image: Optional[str] = None
    music: Optional[str] = None
    sound: Optional[str] = None


class SubtitleRef(BaseModel):
    id: str = ""
    start: int = 0
    end: int = 0


class AnimationData(BaseModel):
    animations: List[Any] = Field(default_factory=list)
    secondaryAnimations: List[Any] = Field(default_factory=list)
    lipSyncs: List[Any] = Field(default_factory=list)
    subtitles: List[SubtitleRef] = Field(default_factory=list)
    media: DialogueMedia = Field(default_factory=DialogueMedia)


class DialogueAction(BaseModel):
    dialogId: Optional[str] = None
    splitterNodeId: Optional[str] = None
    type: str = ""
    needNotification: bool = False
    id: str = ""
    variableId: Optional[str] = None
    value: Optional[Any] = None
    saveScope: Optional[str] = None


class DialogueTrigger(BaseModel):
    type: str = ""
    Conditions: List[Any] = Field(default_factory=list)
    Random: Optional[Dict[str, Any]] = None


class DialogueLine(BaseModel):
    Id: str = ""
    DialogSide: str = ""
    IconType: str = ""
    ConfirmationKey: Optional[str] = None
    AnimationData: AnimationData = Field(default_factory=AnimationData)
    Actions: List[DialogueAction] = Field(default_factory=list)
    Trigger: Optional[DialogueTrigger] = None
    TraderId: str = ""


class Dialogue(BaseModel):
    Id: str = ""
    IsStart: bool = False
    MainVariable: str = ""
    Trader: str = ""
    SubTraders: List[str] = Field(default_factory=list)
    Lines: List[DialogueLine] = Field(default_factory=list)


class DialogueWrapper(BaseModel):
    elements: List[Dialogue]


# ============================================================
# languages/*.json
# ============================================================

Language = Dict[str, str]
