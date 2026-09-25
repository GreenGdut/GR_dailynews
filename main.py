import os
import requests

_ENV_FILE = ".env"

def load_env(path=_ENV_FILE):
    """从本地 .env 文件读取 KEY=VALUE 并写入环境变量。
    文件不存在时静默跳过；占位符(<...>)不载入，避免误用。
    """
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            if key and not value.startswith("<") and key not in os.environ:
                os.environ[key] = value

load_env()

PAT = os.getenv("GITHUB_PAT")
if not PAT:
    raise ValueError("GITHUB_PAT environment variable not set")

PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")
if not PUSHPLUS_TOKEN:
    raise ValueError("PUSHPLUS_TOKEN environment variable not set")

PUSHPLUS_OPTION = os.getenv("PUSHPLUS_OPTION")
if not PUSHPLUS_OPTION:
    raise ValueError("PUSHPLUS_OPTION environment variable not set")


def fetch_note():
    url = "https://api.github.com/repos/GreenGdut/my_knowledge/contents/!_tmp/todo/TODOlist.md"
    headers = {
        "Authorization": f"token {PAT}",
        "Accept": "application/vnd.github.raw"
    }
    resp = requests.get(url,headers=headers)
    resp.raise_for_status()
    return resp.text

def push_note(text:str) -> None:
    payload = {
        "token": PUSHPLUS_TOKEN,
        "title": "TODOLIST",      
        "content": text,             
        "template": "markdown",
        "channel": "webhook",
        "option": PUSHPLUS_OPTION
    }

    resp = requests.post(
        "https://www.pushplus.plus/send",
        json=payload,
        timeout=30
    )
    resp.raise_for_status()

    # PushPlus 即使 HTTP 200，业务码也可能不是 200，需要再检查一次
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"PushPlus 推送失败: {data}")

def main():
    note = fetch_note()
    push_note(note)

if __name__ == "__main__":
    main()

