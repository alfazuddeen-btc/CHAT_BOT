import json
from pathlib import Path
from typing import List

STORE_DIR = Path("app/session_store")
STORE_DIR.mkdir(exist_ok=True)

MAX_SESSION_MESSAGES = 6

def _file(user_id: str) -> Path:
    return STORE_DIR / f"{user_id}.json"

def add_to_session(user_id: str, role: str, content: str):
    history = get_session_context(user_id)
    history.append({"role": role, "content": content})
    history = history[-MAX_SESSION_MESSAGES:]

    with open(_file(user_id), "w") as f:
        json.dump(history, f)

def get_session_context(user_id: str) -> List[dict]:
    file = _file(user_id)
    if not file.exists():
        return []

    try:
        with open(file) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading session: {e}")
        return []

def clear_session(user_id: str):
    file = _file(user_id)
    if file.exists():
        file.unlink()