from pathlib import Path
import requests

def download_latest_source_code_snapshot(
    owner:str,
    repo:str,
    branch:str,
    taget_zip_path:str|Path,
    )->bool:
    if isinstance(taget_zip_path,str):
        taget_zip_path = Path(taget_zip_path)
    url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    response = requests.get(url)
    if response.status_code == 200:
        with taget_zip_path.open('wb') as f:
            f.write(response.content)
        return True
    return False

def get_latest_commit_hash(
    owner:str,
    repo:str,
    branch:str,
)->str|None:
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        latest_commit_hash = data["sha"]
        return latest_commit_hash
    return None