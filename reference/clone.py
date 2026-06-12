import os
import subprocess
from contextlib import suppress
from collections import Counter

script_dir = os.path.dirname(os.path.abspath(__file__))

repos = [
    "https://github.com/the-hideout/TarkovMonitor",
    "https://github.com/RatScanner/RatScanner",
    "https://github.com/RatScanner/RatEye",
    "https://github.com/RatScanner/RatStash",
    "https://github.com/the-hideout/tarkov-dev",
    "https://github.com/the-hideout/tarkov-dev-svg-maps",
    "https://github.com/the-hideout/tarkov-api",
    "https://github.com/TarkovTracker/tarkovdata",
    "https://github.com/carlsmei/tarkovdata",
    "https://github.com/M4elstr0m/TarkovMapTracker",
    "https://github.com/karpitony/eft-where-am-i",
    "https://github.com/adrian-griffin/tilda-eft",
    "https://github.com/kthenwhythen/tarkov-market-helper",
    "https://github.com/milainlambers/EFT-CaseCompilator-Screenshot-Cropper-Combinator",
    "https://github.com/tiltysola/tarkov-tilty-frontend-opensource",
    "https://github.com/tiltysola/magic-mana-client-opensource",
]

names = [repo.rstrip("/").split("/")[-1] for repo in repos]
counts = Counter(names)

for repo in repos:
    with suppress(subprocess.CalledProcessError):
        parts = repo.rstrip("/").split("/")
        owner, reponame = parts[-2], parts[-1]
        dirname = f"{owner}_{reponame}" if counts[reponame] > 1 else reponame

        repo_path = os.path.join(script_dir, dirname)

        if os.path.exists(repo_path):
            subprocess.run(["git", "-C", repo_path, "pull"])
        else:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo, dirname],
                cwd=script_dir,
                check=True
            )