from importlib.metadata import metadata
from pathlib import Path
from typing import Final

from platformdirs import user_cache_dir

_meta = metadata("tarkovtool")
PROJECT_NAME:Final[str] = _meta["Name"]
PROJECT_VERSION:Final[str] = _meta["Version"]

DATA_CACHE_DIR:Final[Path] = Path(user_cache_dir("tarkov_tool_cache"))
DATA_CACHE_DIR.mkdir(parents=True,exist_ok=True)

REFERENCE_DATA_CACHE_DIR:Final[Path] = DATA_CACHE_DIR / 'reference'
REFERENCE_DATA_CACHE_DIR.mkdir(exist_ok=True)