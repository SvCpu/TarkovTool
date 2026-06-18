from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator

# _log prefix model correspond game log format(Got notification | ChatMessageReceived)

# templateId
# 5914450f86f7744bb83be8a2 0|1|2 insuranceStart
# 5914451a86f7744c2d7102f9 0|1|2 insuranceStart with Therapist

# uid/dialogId
# player account id in player message
# Provide services:
# 54cb57776803fa99248b456e Therapist
# 59e7125688a45068a6249071 System
# 656f0f98d80a697f855d34b1 BTR Driver
# 579dc571d53a0658a154fbec Fence
# 5c0647fdd443bc2504c2d371 Jaeger
# 638f541a29ffd1183d187f57 Lightkeeper
# 5a7c2eca46aef81a7ca2145d Mechanic
# 5935c25fb3acc3127c3d8cd9 Peacekeeper
# 54cb50c76803fa8b248b4571 Prapor
# 5ac3b934156ae10c4430e83c Ragman
# 6617beeaa9cfa777ca915b7c Ref
# 58330581ace78e27b8b10cee Skier
# Plot characters:
# 68fe15990f29ba3fdbba9d55 Radio station
# 69e0d6cc77b63940375b9173 Survivor
# 68fe15910f29ba3fdbba9d54 Taran
# 688246518448b05efd61d461 Mr. Kerman
# 688246958448b05efd61d462 Voevoda

class Type(Enum):
    PlayerMessage = 1
    Insurance = 2
    FleaMarket = 4
    SystemMessage = 7
    InsuranceReturn = 8
    TaskStarted = 10
    TaskFailed = 11
    TaskFinished = 12
    CoOpExtractionReward = 13 # this type only has 1 in logs sample; but mark Twitch Drop in other project
    # TwitchDrop = 13
    BTRItemExtraction = 15
    @classmethod
    def from_value(cls, value: int) -> Optional["Type"]:
        return cls._value2member_map_.get(value)

class _log_item_data(BaseModel):
    _id: str
    _tpl: str
    upd:Optional[dict] = Field(default_factory=dict)
    parentId:str
    slotId:str

class _log_items(BaseModel):
    stash:str
    data:list[_log_item_data]

class _log_message_base(BaseModel):
    type: Type
    _id: str
    uid: str
    text: str
    dt:int
    templateId: Optional[str] = None
    maxStorageTime: Optional[int] = None
    hasRewards:bool

class _log_player_message(_log_message_base):
    type: Literal[Type.PlayerMessage]

class _log_insurance_system_data(BaseModel):
    date: str
    time: str
    location: str

class _log_insurance_message(_log_message_base):
    type: Literal[Type.Insurance]
    systemData: _log_insurance_system_data
    items:Optional[_log_items] = Field(default=None)

class _log_fleamarket_message(_log_message_base):
    class system_data(BaseModel):
        buyerNickname: str
        soldItem: str
        itemCount: int
    type: Literal[Type.FleaMarket]
    systemData: Optional[system_data] = Field(default=None)
    items:_log_items

class _log_system_message_message(_log_message_base):
    type: Literal[Type.SystemMessage]
    items:Optional[_log_items] = Field(default=None)

class _log_insurancereturn_message(_log_message_base):
    type: Literal[Type.InsuranceReturn]
    systemData: _log_insurance_system_data
    items:_log_items

class _log_task_started_message(_log_message_base):
    type: Literal[Type.TaskStarted]
    items:Optional[_log_items] = Field(default=None)

class _log_task_failed_message(_log_message_base):
    type: Literal[Type.TaskFailed]

class _log_task_finished_message(_log_message_base):
    type: Literal[Type.TaskFinished]
    items:Optional[_log_items] = Field(default=None)

class _log_co_op_extraction_reward_message(_log_message_base):
    type: Literal[Type.CoOpExtractionReward]
    items:Optional[_log_items] = Field(default=None)

class _log_btr_item_extraction_message(_log_message_base):
    type: Literal[Type.BTRItemExtraction]
    items:Optional[_log_items] = Field(default=None)

_log_message_union = Annotated[Union[
    _log_player_message,
    _log_insurance_message,
    _log_fleamarket_message,
    _log_system_message_message,
    _log_insurancereturn_message,
    _log_task_started_message,
    _log_task_failed_message,
    _log_task_finished_message,
    _log_co_op_extraction_reward_message,
    _log_btr_item_extraction_message,
    ], 
    Field(discriminator="type")]

class _log_model(BaseModel):
    type: Literal['new_message']
    eventId: str # unique id
    dialogId: str
    message: _log_message_union
    @field_validator("message", mode="before")
    def convert_type_int_to_enum(cls, v):
        if isinstance(v, dict) and isinstance(v.get("type"), int):
            v["type"] = Type.from_value(v["type"])
        return v

class Message(BaseModel):
    type: Type
