# modules/pda_store.py
import json
import os
from datetime import datetime
from uuid import uuid4

PDA_PATH = os.path.join("data", "pda_actions.json")


def _ensure_store():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(PDA_PATH):
        with open(PDA_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def load_actions():
    _ensure_store()
    with open(PDA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_actions(actions):
    _ensure_store()
    with open(PDA_PATH, "w", encoding="utf-8") as f:
        json.dump(actions, f, ensure_ascii=False, indent=2)


def add_action(payload: dict) -> str:
    actions = load_actions()

    row = dict(payload)
    row["id"] = row.get("id") or str(uuid4())
    row["created_at"] = row.get("created_at") or datetime.utcnow().isoformat(timespec="seconds")
    row.setdefault("updated_at", None)

    actions.append(row)
    save_actions(actions)
    return row["id"]


def update_action(action_id: str, patch: dict) -> bool:
    actions = load_actions()
    for a in actions:
        if a.get("id") == action_id:
            a.update(patch)
            a["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
            save_actions(actions)
            return True
    return False


def delete_action(action_id: str) -> bool:
    actions = load_actions()
    new_actions = [a for a in actions if a.get("id") != action_id]
    if len(new_actions) != len(actions):
        save_actions(new_actions)
        return True
    return False
