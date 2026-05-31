from .datamodel import GamePurchaseVersion, Location, LogVersion, Raid, Version
from .datamodel import RaidSession, RaidGroup, RaidStatus, RaidType
from .datamodel import Player, Profile, ProfileSide, ProfileType
from ..config import Config
from tarkov_tool.event_manger import EventManger
from ..events import *
from .locations.map import get as get_location

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Final, overload
from contextlib import suppress
from pathlib import Path
import hashlib
import json
import re
import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)

@dataclass
class StatusMark:
    is_local:bool = field(default=False)
    is_online:bool = field(default=False)
    is_pmc:bool = field(default=False)
    is_pve:bool = field(default=False)
    now_profile_id: str = field(default='')
    raid_short_id:str = field(default=None)
    raid_started: bool = field(default=False)
    location: Location = field(default=None)
    map_load_time:float = field(default=None)

class _health_data(BaseModel):
    Current: float
    Maximum: int

class _bodyparts(BaseModel):
    Head: Dict[str, _health_data]
    Chest: Dict[str, _health_data]
    Stomach: Dict[str, _health_data]
    LeftArm: Dict[str, _health_data]
    RightArm: Dict[str, _health_data]
    LeftLeg: Dict[str, _health_data]
    RightLeg: Dict[str, _health_data]

class _player_health(BaseModel):
    Hydration: _health_data
    Energy: _health_data
    Temperature: _health_data
    BodyParts: _bodyparts

class _player_info(BaseModel):
    Nickname: str
    Side: str
    Level: int
    GameVersion: str
    Health: _player_health

class _player(BaseModel):
    aid:int
    Info: _player_info
    isLeader:bool = Field(default=None)

@dataclass
class Log_line:
    time:datetime
    message:str = field(repr=False)
    data:dict|None
    log_path:Path|None = field(default=None)
    line_range:tuple[int,int]|None = field(default=None, repr=False)
    parse_message:str = field(default=None)
    def __hash__(self):
        return hash((self.time, self.message, self.parse_message))
    def __eq__(self, other:'Log_line'):
        return (self.time, self.message, self.parse_message) == (other.time, other.message, other.parse_message)

class LogParser:
    _log_pattern:str
    _timestamp_format:str
    _max_member: int
    _global_event_mark = False
    _parse_strings:tuple[str]
    @overload
    def __new__(self,version:Version|str, live_mode=False):...
    def __new__(cls, *args, **kwargs):
        cls = ReleaseLogParser
        if version:=kwargs.get('version'):
            if isinstance(version, str):
                version = Version(version)
            if not isinstance(version, Version):
                raise TypeError
            cls = ReleaseLogParser if version >= Version('1.0.0.0.41787') else BetaLogParser
        return object.__new__(cls)
    def __init__(self, *args, **kwargs):
        self._enable_event_trigger:False
        self._player_name_index:dict[str,Player] = {}
        self._player_aid_index:dict[str,Player] = {}
        self.live_mode:bool = kwargs.get("live_mode", False)
        self.raids:list[Raid] = []
        self.recordingraidindex:int|None = None
        self.ac_player:Player = Player()
        self.other_player:list[Player] = []
        self._log_lines:list[Log_line] = []
        self._parsed = False
        self._raid_mark = StatusMark()
        self.new_group()
    @staticmethod
    def sensitive_data_hash(data:str)->str:
        if Config.enable_sensitive_data_hashing_for_tarkov:
            if data:
                if not isinstance(data, str):
                    data = str(data)
                h = hashlib.blake2b(digest_size=6)
                h.update(data.encode('utf-8'))
                return h.hexdigest()
        return data
    @property
    def now_raid(self)->Raid|None:
        if self.recordingraidindex is None:
            return None
        else:
            return self.raids[self.recordingraidindex]
    def new_log_folder(self):
        '表示之後傳入的日誌都是新的日誌資料夾產生的'
    def raid_done(self):
        self._raid_mark = StatusMark()
        if self.now_raid is not None:
            self.recordingraidindex = None
    def new_raid(self):
        self._raid_mark = StatusMark()
        self.raids.append(Raid())
        if self.now_raid is None:
            self.recordingraidindex = len(self.raids) - 1
        else:
            self.recordingraidindex += 1
    def new_group(self):
        self.raid_group:RaidGroup = RaidGroup(max_member=self._max_member)
    def enable_event(self):
        if self._global_event_mark:
            raise Exception('同一時間只能有一個解析器可以啟用事件觸發')
        self._global_event_mark = True
        self._enable_event_trigger = True
    def disable_event(self):
        if self._enable_event_trigger:
            self._enable_event_trigger = False
        if self._global_event_mark:
            self._global_event_mark = False
    def _event_trigger(self, event:Event):
        if self._enable_event_trigger:
            EventManger._trigger(event=event)
    def add_line(self, line:Log_line):
        self._log_lines.append(line)
    def add_lines(self, lines:list[Log_line]):
        self._log_lines.extend(lines)
    @staticmethod
    def build_line_index(data: str) -> list[tuple[int, int]]:
        lines = data.splitlines(True)
        index = []
        current_pos = 0
        for line in lines:
            start = current_pos
            end = start + len(line)
            index.append((start, end))
            current_pos = end
        return index
    @staticmethod
    def get_line_range(data: str, match_start: int, match_end: int) -> tuple[int, int]:
        lines = data.splitlines(True)
        current_pos = 0
        start_line = end_line = 0
        for i, line in enumerate(lines):
            line_start = current_pos
            line_end = current_pos + len(line)
            if match_start >= line_start and match_start < line_end:
                start_line = i + 1
            if match_end > line_start and match_end <= line_end:
                end_line = i + 1
            current_pos = line_end
        return start_line, end_line
    @staticmethod
    def get_line_range_from_index(index_list: list[tuple[int, int]], match_start: int, match_end: int) -> tuple[int, int]:
        start_line = end_line = 0
        for i, (start, end) in enumerate(index_list):
            if start <= match_start < end:
                start_line = i + 1
            if start < match_end <= end:
                end_line = i + 1
            if start_line and end_line:
                break
        return start_line, end_line
    def parse_data(self, data:str, log_path:Path=None, line_index:bool=False)->tuple[Log_line]:
        if line_index:
            line_indexs = self.build_line_index(data)
        out:list[Log_line] = []
        log_messages = re.finditer(self._log_pattern, data, re.MULTILINE)

        for match in log_messages:
            match_start = match.start()
            match_end = match.end()
            date = match.group("date")
            time = match.group("time")
            message = match.group("message")
            json_part = match.group("json") if match.group("json") else None
            dt_string = f"{date} {time}"
            if parse_message:=next((x for x in self._parse_strings if x in message), False):
                try:
                    timestamp = datetime.strptime(dt_string, self._timestamp_format)
                except ValueError as e:
                    print(f"無法解析時間：{dt_string} → {e}")
                    continue
                line = Log_line(time=timestamp,message=message,parse_message=parse_message)
                if json_part:
                    line.data = json.loads(json_part)
                if line_index:
                    line.line_range = self.get_line_range_from_index(line_indexs, match_start, match_end)
                if log_path:
                    line.log_path = log_path
                out.append(line)
        out.sort(key=lambda x: x.time)
        return tuple(out)
    def add_player(self, player:Player):
        if not player.is_player_in(self.other_player):
            self.other_player.append(player)
    def _parse_player_data(self, data:dict)->_player|None:
        with suppress():
            player_data = _player(**data)
            player_data.aid = self.sensitive_data_hash(player_data.aid)
            return player_data
        return None
    def parse_line(self, line:Log_line):
        match line.parse_message:
            case 'Session mode: ':
                '發生在第一次載入Profile和切換模式時'
                if match:= re.search(r"Session mode: (?P<mode>\w+)", line.message):
                    mode = match.group("mode")
                    self.profiletype = ProfileType(mode)
            case 'SelectProfile ProfileId:':
                if self.now_raid:
                    self.recordingraid.end(line.time)
                if match := re.search(r"SelectProfile ProfileId:(?P<pid>\w+)\s+AccountId:(?P<aid>\d+)",line.message):
                    profile_id = self.sensitive_data_hash(match.group("pid"))
                    account_id = self.sensitive_data_hash(match.group("aid"))
                    if not self.ac_player.ac_id:
                        self.ac_player.ac_id = account_id
                    if profile_id:
                        self._raid_mark.now_profile_id = profile_id
                        match profile_id:
                            case self.ac_player.pve_profile_id:
                                self._raid_mark.is_pve = True
                            case self.ac_player.regular_profile_id:
                                self._raid_mark.is_pve = False
            case 'Got notification | GroupMatchInviteAccept':
                '發生在發送邀請的人接受邀請時'
                if line.data:
                    json_data:dict = line.data
                    player_data = self._parse_player_data(line.data)
                    player = Player(
                        ac_id=player_data.aid,
                        nickname=player_data.Info.Nickname,
                    )
                    player.level=player_data.Info.Level
                    with suppress(ValueError):
                        player.side=ProfileSide(player_data.Info.Side)
                    with suppress(ValueError):
                        player.game_purchase_version = GamePurchaseVersion(player_data.Info.GameVersion)
                    self.raid_group.join(player)
                    self.add_player(player)
            case 'Got notification | GroupMatchInviteSend':
                '發生在收到邀請並接受或拒絕邀請時'
                # has Group info
            case 'Got notification | GroupMatchUserLeave':
                '用戶離開小組'
                if line.data:
                    player = Player(
                        ac_id=self.sensitive_data_hash(line.data['aid']),
                        nickname=str(line.data['Nickname'])
                    )
                    self.raid_group.leave(player)
                    self.add_player(player)
            case 'Got notification | GroupMatchWasRemoved':
                '當小組解散時'
                self.new_group()
            case 'Got notification | GroupMatchRaidSettings':
                '當小組負責人邀請成員準備就緒時發生'
                if line.data:
                    if raidSettings:=line.data.get('raidSettings'):
                        self._raid_mark.location = Location(raidSettings['location'])
                        if raidSettings.get('side') == 'Pmc':
                            self._raid_mark.is_pmc = True
            case 'Got notification | GroupMatchRaidReady':
                '當`準備就緒`時, 該事件將發生在群組內其他每個成員身上'
                # can get meber iteminfo
                if line.data:
                    if extendedProfile := line.data('extendedProfile',{}):
                        player_data = self._parse_player_data(extendedProfile)
                        player = Player(
                            ac_id=player_data.aid,
                            nickname=player_data.Info.Nickname,
                        )
                        self.add_player(player)
            case 'application|Matching with group id':
                ''
                if group_id := line.message[line.message.index('Matching with group id: ')+24:]:
                    if group_id:
                        self.raid_group.id = group_id
            case 'Error|Default|[Transit] Flag:Common':
                if match := re.search(r'RaidId:(\w+),.*?Locations:(\w+)', line.message):
                    raid_id = match.group(1)
                    location = match.group(2)
                    if raid_id:
                        self.now_raid.id = raid_id
                    if location:
                        self._raid_mark.location = Location(location)
            case 'application|LocationLoaded':
                '地圖已加載，遊戲正在尋找比賽'
                if match := re.search(r"LocationLoaded:[0-9.,]+ real:(?P<loadTime>[0-9.,]+)", line.message):
                    load_time_str = match.group("loadTime").replace(",", ".")
                    self._raid_mark.map_load_time = float(load_time_str)
            case 'application|MatchingCompleted':
                '''
                已完成配對，並與其他玩家鎖定至同一伺服器
                目前僅有排隊時間可供查看
                該狀況發生於首次載入突襲時，或當使用者取消配對時
                使用者重新連接至進行中的突襲時則不會發生
                '''
                if match := re.search(r"MatchingCompleted:[0-9.,]+ real:(?P<queueTime>[0-9.,]+)", line.message):
                    queue_time_str = match.group("queueTime").replace(",", ".")
                    queue_time = float(queue_time_str)
                else:
                    queue_time = None
                # queue_time can't find in 
            case 'application|TRACE-NetworkGameCreate profileStatus':
                '''
                配對完成後立即觸發
                可用資訊已足夠，可引發 MatchFound 事件
                only online
                '''
                if "RaidMode: Online" in line.message:
                    self._raid_mark.is_online = True
                if map_match := re.search(r"Location: (?P<map>[^,]+)", line.message):
                    map = map_match.group("map")
                    self._raid_mark.location = Location(map)
                if raid_id_match := re.search(r"shortId: (?P<shortId>[A-Z0-9]{6})", line.message):
                    raid_id = raid_id_match.group("shortId")
                    self._raid_mark.raid_short_id = raid_id
                # # 判斷是否為 Reconnect 狀態
                # if raid_id in raids:
                #     raid_info = raids[raid_id]
                #     reconnected = True
                # else:
                #     raids[raid_id] = raid_info
                #     reconnected = False

                # # 觸發 MatchFound（排除重連且有排隊時間）
                # if not reconnected and online and getattr(raid_info, "queue_time", 0) > 0:
                #     if match_found_callback:
                #         match_found_callback(raid_info, current_profile)

                # # 一律觸發 MapLoaded
                # if map_loaded_callback:
                #     map_loaded_callback(raid_info, current_profile)
            case 'application|GameStarting':
                '''
                GameStarting always happens for PMCs and sometimes happens for scavs.
                For PMCs, it corresponds with the start of the countdown timer.
                '''
                self.recordingraid.starting(line.time)
            case 'application|GameStarted':
                'Raid begins, either at the end of the countdown for PMC, or immediately as a scav'
                self.recordingraid.started(line.time)
                self.recordingraid.ispmc = self.RaidSettings.get('pmc',self.recordingraid.ispmc)
                self.recordingraid.Sid = self.RaidSettings.get('sid',self.recordingraid.Sid)
                self.recordingraid.location = self.RaidSettings.get('location',self.recordingraid.location)
                self.recordingraid.id = self.RaidSettings.get('rid',self.recordingraid.id)
                self.recordingraid.onlinemode = self.RaidSettings.get('online',self.recordingraid.onlinemode)

            case 'application|Network game matching aborted'|'application|Network game matching cancelled':
                '用戶取消匹配'
            case 'Got notification | UserMatchOver':
                '使用者配對結束'
                self.RaidSettings['online'] = True
                if line.json_data:
                    json_data:dict = json.loads(line.json_data)
                    if location_str := json_data.get('location'):
                        self.RaidSettings['location'] = Location(location_str)
                    if sid := json_data.get('shortId'):
                        self.RaidSettings['sid'] = sid
            case 'application|Init: pstrGameVersion: ':
                '遊戲初始化時發出一條'
                # application.log | traces.log
                #'Escape from Tarkov 0.16.8.0.37972, uiAddress: 0, usPort: 0'
                game_version = line.message[line.message.rindex('pstrGameVersion: ')+17:line.message.index(',')]
                # print(game_version)
                # if self.raidrecording:
                #     self.recordingraid.end(line.time)
            case 'Got notification | ChatMessageReceived':
                if line.json_data:
                    jsdata:dict = json.loads(line.json_data)
                    type:int = jsdata.get('message',{}).get('type')
                    if typeenum := MessageType.from_value(type):
                        # print(typeenum.name)
                        message_data:dict = jsdata['message']
                        templateId = message_data.get('templateId')
                        match typeenum:
                            case MessageType.PlayerMessage:
                                pass
                            case MessageType.FleaMarket:
                                ''
                                if templateId:
                                    match templateId:
                                        case '5bdabfb886f7743e152e867e 0':
                                            '跳蚤市場出售'
                                        case '5bdabfe486f7743e1665df6e 0':
                                            '跳蚤市場報價已過期'
                                    # self.t.add(templateId)
                                    # print(locals().keys())
                        # if templateId := message_data.get('templateId'):
                        #     self.t.add(templateId)
                    # else:
                    #     print(type)
            case 'application|scene preset path:maps':
                if bundleMatch := re.search(r"scene preset path:maps/(?P<mapBundleName>[a-zA-Z0-9_]+)\.bundle", line.message):
                    mapBundle = bundleMatch.group("mapBundleName")
                    location:Location = Location(get_location(mapBundle))
        # if line.parse_message == 'Got notification | ChatMessageReceived':
        #     return
        # self.t.append((line.time,line.message))


class BetaLogParser(LogParser):
    _log_pattern = r"(?P<date>^\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}\.\d{3} [+-]\d{2}:\d{2})\|(?P<message>.+$)\s*(?P<json>^{[\s\S]+?^})?"
    _timestamp_format = "%Y-%m-%d %H:%M:%S.%f %z"
    _max_member = 5
    _parse_strings:Final[tuple[str]] = (
    'Session mode: ',
    'SelectProfile ProfileId:',
    'Got notification | GroupMatchInviteAccept',
    'Got notification | GroupMatchInviteSend',
    'Got notification | GroupMatchUserLeave',
    'Got notification | GroupMatchWasRemoved',
    'Got notification | GroupMatchRaidSettings',
    'Got notification | GroupMatchRaidReady',
    'application|Matching with group id',
    'application|LocationLoaded',
    'application|MatchingCompleted',
    'application|TRACE-NetworkGameCreate profileStatus',
    'application|GameStarting',
    'application|GameStarted',
    'application|Network game matching aborted',
    'application|Network game matching cancelled',
    'Got notification | UserMatchOver',
    'application|Init: pstrGameVersion: ',
    'Got notification | ChatMessageReceived',
    'Error|Default|[Transit] Flag:Common',
    'application|scene preset path:maps',
    )

class ReleaseLogParser(LogParser):
    _log_pattern = r"(?P<date>^\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}\.\d{3})\|(?P<message>.+$)\s*(?P<json>^{[\s\S]+?^})?"
    _timestamp_format = "%Y-%m-%d %H:%M:%S.%f"