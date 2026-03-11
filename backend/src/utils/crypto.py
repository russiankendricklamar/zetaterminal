"""
Symmetric encryption for API keys stored in the database.

Uses Fernet (AES-128-CBC with HMAC-SHA256) from the cryptography library.
The encryption key is derived from the existing JWT_SECRET env var.
"""
import base64
import hashlib
import logging
import os

logger = logging.getLogger(__name__)

_fernet = None


def _get_fernet():
    """Lazy-init Fernet cipher from JWT_SECRET."""
    global _fernet
    if _fernet is not None:
        return _fernet

    try:
        from cryptography.fernet import Fernet
    except ImportError:
        logger.warning("cryptography not installed — API key encryption disabled")
        return None

    secret = os.getenv("JWT_SECRET", "")
    if not secret:
        logger.warning("JWT_SECRET not set — API key encryption disabled")
        return None

    # Derive a 32-byte key from JWT_SECRET via SHA-256, then base64-encode for Fernet
    key_bytes = hashlib.sha256(secret.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    _fernet = Fernet(fernet_key)
    return _fernet


def encrypt_value(plaintext: str) -> str:
    """Encrypt a plaintext string. Raises if encryption is unavailable."""
    f = _get_fernet()
    if f is None:
        raise RuntimeError(
            "Encryption unavailable — install 'cryptography' and set JWT_SECRET"
        )
    return f.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    """Decrypt a ciphertext string. Returns the plaintext."""
    f = _get_fernet()
    if f is None:
        raise RuntimeError(
            "Decryption unavailable — install 'cryptography' and set JWT_SECRET"
        )
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except Exception:
        logger.warning("Failed to decrypt value — possible legacy unencrypted data")
        raise
