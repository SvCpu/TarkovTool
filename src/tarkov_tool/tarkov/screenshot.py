from .datamodel import ScreenshotInfo, Position

from datetime import datetime
import re
import math
from pathlib import Path
from typing import Iterable

__all__ = [
    'get_screenshot_info',
    'generate_screenshot_filename',
    'generate_unique_screenshot_filename',
]

def generate_screenshot_filename(index: int = 0)->str:
    now = datetime.now()
    filename = now.strftime(f"%Y-%m-%d[%H-%M] ({index}).png")
    return filename

def generate_unique_screenshot_filename(existing: Iterable[str]) -> str:
    existing = set(existing)
    index = 0
    while True:
        filename = generate_screenshot_filename(index)
        if filename not in existing:
            return filename
        index += 1

def get_screenshot_info(filepath:Path)->ScreenshotInfo|None:
    if not isinstance(filepath,Path):
        raise TypeError
    if filepath.suffixes != '.png':
        return None
    info = ScreenshotInfo(filepath=filepath, filename=filepath.name)
    def quaternions_to_yaw(rx: float, ry: float, rz: float, rw: float) -> float:
        siny_cosp = 2 * (rw * rz + rx * ry)
        cosy_cosp = 1 - 2 * (ry * ry + rz * rz)
        return math.degrees(math.atan2(siny_cosp, cosy_cosp))

    def quaternions_to_pitch(rx: float, ry: float, rz: float, rw: float) -> float:
        sinp = 2 * (rw * ry - rz * rx)
        if abs(sinp) >= 1:
            pitch_rad = math.copysign(math.pi / 2, sinp)
        else:
            pitch_rad = math.asin(sinp)
        return math.degrees(pitch_rad)

    match = re.match(
        r"^\d{4}-\d{2}-\d{2}\[\d{2}-\d{2}\]_"
        r"(?P<x>-?\d+\.\d+), (?P<y>-?\d+\.\d+), (?P<z>-?\d+\.\d+)_"
        r"(?P<rx>-?\d+\.\d+), (?P<ry>-?\d+\.\d+), (?P<rz>-?\d+\.\d+), (?P<rw>-?\d+\.\d+)_"
        r"(?P<angle>-?\d+\.\d+) \(\d\)\.png$",
        filepath.name
    )
    if match:

        x = float(match.group("x"))
        y = float(match.group("y"))
        z = float(match.group("z"))
        rx = float(match.group("rx"))
        ry = float(match.group("ry"))
        rz = float(match.group("rz"))
        rw = float(match.group("rw"))

        info.yaw = quaternions_to_yaw(rx, ry, rz, rw)
        info.pitch = quaternions_to_pitch(rx, ry, rz, rw)
        info.position = Position(x=x, y=y, z=z)

    return info