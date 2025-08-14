import json
import os
from typing import Dict, List, Optional


_USERS: Dict[str, str] = {}


def _get_users_file_path() -> str:
  default_path = os.path.join(os.path.dirname(__file__), "users.json")
  return os.getenv("USERS_FILE", default_path)


def load_users() -> None:
  global _USERS
  path = _get_users_file_path()
  if not os.path.exists(path):
    _USERS = {}
    return
  with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
  # Expecting { "users": [ {"email": "...", "password": "..."}, ... ] }
  users_map: Dict[str, str] = {}
  for item in data.get("users", []):
    email = item.get("email")
    password = item.get("password")
    if email and password:
      users_map[email.lower()] = password
  _USERS = users_map


def verify_user(email: str, password: str) -> bool:
  if not _USERS:
    load_users()
  stored = _USERS.get(email.lower())
  return stored is not None and stored == password


def list_user_emails() -> List[str]:
  if not _USERS:
    load_users()
  return list(_USERS.keys())


