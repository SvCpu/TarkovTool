from enum import Enum
from pydantic import BaseModel, ConfigDict, computed_field
from datetime import datetime
from pathlib import Path

from .datamodel import ScreenshotInfo

class EventBase(BaseModel):
    event_time: datetime
    model_config = ConfigDict(
        validate_assignment=True,
        json_encoders={Path: str}
    )
    @computed_field
    @property
    def event_name(self)->str:
        return self.__class__.__name__

class ON_STARTUP(EventBase):
    '主程式啟動時觸發'

class ON_SHUTDOWN(EventBase):
    '主程式關閉時觸發'

class TARKOV_RAID_START(EventBase):
    '塔科夫戰局開始時觸發'

class TARKOV_START(EventBase):
    '塔科夫主程序啟動時觸發'

class TARKOV_SCREENSHOT(EventBase):
    '塔科夫遊戲內截圖時觸發'
    info: ScreenshotInfo
    path: Path

class TARKOV_MAP_SWITCH(EventBase):
    '''塔科夫遊戲切換地圖時觸發
    注意: 只有在地圖與上一次觸發的地圖不一樣時才會觸發
    '''

ALL_EVENTS = set(EventBase.__subclasses__())