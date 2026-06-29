from enum import Enum

from pydantic import BaseModel

class Location(Enum):
    Lighthouse = 'Lighthouse'
    TarkovStreets = 'TarkovStreets'
    Shoreline = 'Shoreline'
    Reserve = 'Reserve'
    GroundZeroHigh = 'GroundZero_High'
    GroundZero = 'GroundZero'
    FactoryDay = 'Factory_Day'
    FactoryNight = 'Factory_Night'
    Woods = 'Woods'
    Interchange = 'Interchange'
    Labs = 'Labs'
    Customs = 'Customs'
    Icebreaker = 'Icebreaker'
    Terminal = 'Terminal'

class Extraction(BaseModel):
    name:str
    faction:list[str]
    always_available:bool
    '總是可用'
    single_use:bool
    '一次性撤離點'
    Requirements:str

class LocationData(BaseModel):
    name:Location
    bundle_map:str
    location_map:str
    ingameversion:str
    size:tuple[int,int]
    Extractions:list[Extraction]