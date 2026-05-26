from __future__ import annotations
import secrets
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return {}


def generate_api_key() -> tuple[str, str, str]:
    raw_key = "sk_" + secrets.token_urlsafe(48)
    prefix = raw_key[:10]
    key_hash = pwd_context.hash(raw_key)
    return raw_key, prefix, key_hash


def verify_api_key(raw_key: str, key_hash: str) -> bool:
    return pwd_context.verify(raw_key, key_hash)


_fernet = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = settings.encryption_key
        if len(key) != 44:
            key = Fernet.generate_key()
        _fernet = Fernet(key if isinstance(key, bytes) else key.encode())
    return _fernet


def encrypt_value(value: str) -> str:
    f = _get_fernet()
    return f.encrypt(value.encode()).decode()


def decrypt_value(encrypted_value: str) -> str:
    f = _get_fernet()
    return f.decrypt(encrypted_value.encode()).decode()
