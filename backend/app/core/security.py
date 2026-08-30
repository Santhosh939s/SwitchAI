import base64
import datetime
from typing import Optional
import bcrypt
from cryptography.fernet import Fernet
from jose import JWTError, jwt
from app.core.config import settings

def _get_fernet() -> Fernet:
    key = settings.ENCRYPTION_KEY
    # Ensure key is 32-byte base64 encoded for Fernet
    if len(key) != 44:
        # Pad or derive 32-byte key
        raw_bytes = key.encode('utf-8').ljust(32, b'0')[:32]
        key_b64 = base64.urlsafe_b64encode(raw_bytes).decode('utf-8')
    else:
        key_b64 = key
    return Fernet(key_b64)

def encrypt_key(plain_key: str) -> str:
    f = _get_fernet()
    return f.encrypt(plain_key.encode('utf-8')).decode('utf-8')

def decrypt_key(encrypted_key: str) -> str:
    f = _get_fernet()
    return f.decrypt(encrypted_key.encode('utf-8')).decode('utf-8')

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')[:72]
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
