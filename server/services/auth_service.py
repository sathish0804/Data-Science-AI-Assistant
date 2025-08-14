import os
import time
import hmac
import hashlib
import base64
from typing import Optional

from pydantic import EmailStr
from persistence.user_store import verify_user


def _get_jwt_secret() -> str:
  secret = os.getenv("JWT_SECRET", "change-me")
  return secret


def _base64url_encode(data: bytes) -> str:
  return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data: str) -> bytes:
  padding = '=' * (-len(data) % 4)
  return base64.urlsafe_b64decode(data + padding)


def _sign(header_payload: str, secret: str) -> str:
  signature = hmac.new(secret.encode(), header_payload.encode(), hashlib.sha256).digest()
  return _base64url_encode(signature)


def generate_jwt(email: EmailStr, ttl_seconds: int = 60 * 60 * 8) -> str:
  header = {"alg": "HS256", "typ": "JWT"}
  now = int(time.time())
  payload = {"sub": str(email), "iat": now, "exp": now + ttl_seconds}

  import json

  header_b64 = _base64url_encode(json.dumps(header, separators=(',', ':')).encode())
  payload_b64 = _base64url_encode(json.dumps(payload, separators=(',', ':')).encode())
  header_payload = f"{header_b64}.{payload_b64}"
  signature = _sign(header_payload, _get_jwt_secret())
  return f"{header_payload}.{signature}"


def verify_jwt(token: str) -> Optional[str]:
  try:
    header_b64, payload_b64, signature = token.split('.')
    header_payload = f"{header_b64}.{payload_b64}"
    expected_sig = _sign(header_payload, _get_jwt_secret())
    if not hmac.compare_digest(signature, expected_sig):
      return None

    import json
    payload = json.loads(_base64url_decode(payload_b64))
    if int(time.time()) > int(payload.get("exp", 0)):
      return None
    return payload.get("sub")
  except Exception:
    return None


def authenticate_user(email: EmailStr, password: str) -> bool:
  return verify_user(str(email), password)


