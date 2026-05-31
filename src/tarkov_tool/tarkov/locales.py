from pathlib import Path
import importlib.resources as resources

locales_dir = resources.files("tarkov_tool.tarkov.localization")

print(list(locales_dir.iterdir()))