from .util.github import *
from .constants import REFERENCE_DATA_CACHE_DIR

import shutil
from functools import lru_cache
from datetime import datetime
import json
from zipfile import ZipFile

from pydantic import BaseModel, Field, field_serializer

class _reference_cache_info(BaseModel):
    cache_name: str
    last_commit_hash:str
    last_update: datetime = Field(default_factory=datetime.now)
    @field_serializer("last_update")
    def serialize_timestamp(self, value):
        return value if value is not None else datetime.now()

class _reference_cache_info_file(BaseModel):
    infos:dict[str, _reference_cache_info] = Field(default_factory=dict)
    last_update: datetime = Field(default_factory=datetime.now)
    @field_serializer("last_update")
    def serialize_timestamp(self, value):
        return value if value is not None else datetime.now()

class _reference:
    _owner:str
    _repo:str
    _branch:str
    _cache_name:str
    _cache_info_path = REFERENCE_DATA_CACHE_DIR / 'cache_info.json'
    _cache_infos:_reference_cache_info_file = None
    @classmethod
    def load_info_file(cls):
        if not cls._cache_info_path.exists():
            cls._cache_info_path.touch()
        if data := cls._cache_info_path.read_text(encoding="utf-8"):
            data = json.loads(cls._cache_info_path.read_text(encoding="utf-8"))
            cls._cache_infos = _reference_cache_info_file(**data)
        else:
            cls._cache_infos = _reference_cache_info_file()
    @classmethod
    def save_info_file(cls):
        if not cls._cache_info_path.exists():
            cls._cache_info_path.touch()
        if cls._cache_infos:
            cls._cache_infos.last_update = None
            cls._cache_info_path.write_text(cls._cache_infos.model_dump_json(ensure_ascii=False), encoding='utf-8')
    @classmethod
    @lru_cache(maxsize=1)
    def path(cls)->Path:
        return REFERENCE_DATA_CACHE_DIR / cls._cache_name
    @classmethod
    def download(cls):
        d_path = REFERENCE_DATA_CACHE_DIR / f'{cls._cache_name}.zip'
        if download_latest_source_code_snapshot(
            owner=cls._owner,
            repo=cls._repo,
            branch=cls._branch,
            taget_zip_path=d_path
            ):
            with ZipFile(d_path, "r") as zf:
                zf.extractall(cls.path())
            top_level = next(Path(cls.path()).iterdir())
            for item in top_level.iterdir():
                shutil.move(str(item), cls.path())
            shutil.rmtree(top_level)
            d_path.unlink()
            cls._cache_infos.infos[cls._cache_name] = _reference_cache_info(
                cache_name=cls._cache_name,
                last_commit_hash= get_latest_commit_hash(cls._owner, cls._repo, cls._branch)
            )
            cls._download_postprocess()
            cls.save_info_file()
    @classmethod
    def check(cls):
        if cls._cache_infos is None:
            cls.load_info_file()
        if cls.path().exists():
            cls.updata()
        else:
            cls.download()
    @classmethod
    def updata(cls):
        if cache_info:=cls._cache_infos.infos.get(cls._cache_name):
            latest_commit_hash = get_latest_commit_hash(cls._owner, cls._repo, cls._branch)
            if latest_commit_hash != cache_info.last_commit_hash:
                cls.download()
        else:
            cls.download()
    @classmethod
    def _download_postprocess(cls):...
    @classmethod
    def _rmtree(cls, path:Path):
        if path.is_relative_to(cls.path()):
            if path.is_dir():
                shutil.rmtree(path)
    @classmethod
    def _rm(cls, path:Path):
        if path.is_relative_to(cls.path()):
            if path.is_file():
                path.unlink()

class carlsmei_tarkovdata(_reference):
    _cache_name = 'carlsmei_tarkovdata'
    _owner = 'carlsmei'
    _repo = 'tarkovdata'
    _branch = 'main'
    @classmethod
    def _download_postprocess(cls):
        cls._rmtree(cls.path()/ '.github')
        cls._rmtree(cls.path()/ 'scripts')
class TarkovTracker_tarkovdata(_reference):
    _cache_name = 'TarkovTracker_tarkovdata'
    _owner = 'TarkovTracker'
    _repo = 'tarkovdata'
    _branch = 'master'
    @classmethod
    def _download_postprocess(cls):
        cls._rmtree(cls.path()/'.github')