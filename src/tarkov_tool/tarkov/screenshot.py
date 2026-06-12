from .datamodel import ScreenshotInfo, Position

import re
import math
from pathlib import Path

def get_screenshot_info_from_filename(filename:Path)->ScreenshotInfo|None:
    if not isinstance(filename,Path):
        raise TypeError
    filename:str = filename.name
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
        filename
    )
    if not match:
        return None

    x = float(match.group("x"))
    y = float(match.group("y"))
    z = float(match.group("z"))
    rx = float(match.group("rx"))
    ry = float(match.group("ry"))
    rz = float(match.group("rz"))
    rw = float(match.group("rw"))

    yaw = quaternions_to_yaw(rx, ry, rz, rw)
    pitch = quaternions_to_pitch(rx, ry, rz, rw)
    pos = Position(x, y, z)

    return ScreenshotInfo(filename=filename, position=pos, yaw=yaw, pitch=pitch)