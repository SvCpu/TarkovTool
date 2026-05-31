from .tarkov.datamodel import ScreenshotInfo

from typing import Type
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, computed_field, Field

class Event(BaseModel):
    _event_name = 'base event'
    event_time: datetime = Field(default_factory=datetime.now)
    model_config = ConfigDict(
        validate_assignment=True,
        json_encoders={Path: str}
    )
    def __init_subclass__(cls, **kwargs):
        cls._event_name = cls.__name__
        return super().__init_subclass__(**kwargs)
    @computed_field
    def event_name(self) -> str:
        return self._event_name

class ON_STARTUP(Event):
    '事件偵測啟動時觸發'

class ON_SHUTDOWN(Event):
    '事件偵測關閉時觸發'

class TARKOV_RAID_START(Event):
    '''塔科夫戰局開始時觸發\\
    重新連接戰局也有可能觸發
    '''

class TARKOV_START(Event):
    '塔科夫主程序啟動時觸發'

class TARKOV_SCREENSHOT(Event):
    '塔科夫遊戲內截圖時觸發'
    info: ScreenshotInfo
    path: Path

class TARKOV_PROFILE_SWITCH(Event):
    '''塔科夫遊戲切換Profile時觸發\\
    切換遊戲模式(PVP/PVE)觸發
    '''

class TARKOV_MAP_DETECT(Event):
    '''偵測到塔科夫遊戲地圖時觸發\\
    只要偵測到地圖相關的數據時就會觸發\\
    此事件會更頻繁的被觸發
    '''

class TARKOV_MAP_SWITCH(Event):
    '''塔科夫遊戲切換地圖時觸發\\
    注意: 只有在地圖與上一次觸發的地圖不一樣時才會觸發
    '''

ALL_EVENTS:set[Type[Event]] = set(Event.__subclasses__())