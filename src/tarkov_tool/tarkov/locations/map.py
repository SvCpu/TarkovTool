from typing import Final

map_bundles:Final[dict[str,str]] = {
    "sandbox_start_preset": "Sandbox_Gu",
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

location_map:Final[dict[str,str]] = {
    'Sandbox_Gu': 'Sandbox_Guide',
    'Lighthouse': 'Lighthouse',
    'TarkovStreets': 'TarkovStreets',
    'Shoreline': 'Shoreline',
    'RezervBase': 'Reserve',
    'Sandbox_high': 'GroundZero_High',
    'Sandbox': 'GroundZero',
    'factory4_day': 'Factory_Day',
    'factory4_night' : 'Factory_Night',
    'Woods': 'Woods',
    'Interchange': 'Interchange',
    'laboratory': 'Labs',
    'bigmap': 'Customs',
    'Labyrinth': 'The_Labyrinth',
    'Icebreaker': 'Icebreaker'
}

def get(location_str:str) -> str|None:
    if bundles:=map_bundles.get(location_str):
        return location_map[bundles]
    return location_map.get(location_str, None)