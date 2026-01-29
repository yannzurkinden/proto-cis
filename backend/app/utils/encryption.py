"""Encryption utilities for sensitive data (medical data)."""

import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import get_settings

settings = get_settings()


def _derive_key(secret: str, salt: bytes) -> bytes:
    """Derive encryption key from secret using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(secret.encode()))


def _get_fernet() -> Fernet:
    """Get Fernet instance for encryption/decryption."""
    # Use a fixed salt derived from the secret key for consistency
    salt = settings.secret_key[:16].encode().ljust(16, b"\x00")
    key = _derive_key(settings.secret_key, salt)
    return Fernet(key)


def encrypt_data(data: Optional[str]) -> Optional[str]:
    """Encrypt sensitive data using AES-256 (Fernet)."""
    if data is None or data == "":
        return data

    fernet = _get_fernet()
    encrypted = fernet.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: Optional[str]) -> Optional[str]:
    """Decrypt sensitive data."""
    if encrypted_data is None or encrypted_data == "":
        return encrypted_data

    try:
        fernet = _get_fernet()
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception:
        # If decryption fails, the data may be stored as plaintext (e.g. seed data)
        return encrypted_data
