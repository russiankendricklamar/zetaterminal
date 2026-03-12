"""
Symmetric encryption for API keys stored in the database.

Uses Fernet (AES-128-CBC with HMAC-SHA256) from the cryptography library.
Prefers a dedicated FERNET_KEY env var; falls back to deriving from JWT_SECRET
for backward compatibility with existing encrypted data.
"""
import base64
import hashlib
import logging
import os

logger = logging.getLogger(__name__)

_fernet = None


def _get_fernet():
    """Lazy-init Fernet cipher from FERNET_KEY (preferred) or JWT_SECRET (fallback)."""
    global _fernet
    if _fernet is not None:
        return _fernet

    try:
        from cryptography.fernet import Fernet
    except ImportError:
        logger.warning("cryptography not installed — API key encryption disabled")
        return None

    # Prefer dedicated encryption key, fall back to JWT_SECRET for backward compat
    fernet_key_env = os.getenv("FERNET_KEY", "")
    if fernet_key_env:
        try:
            _fernet = Fernet(fernet_key_env.encode())
            logger.info("Fernet cipher initialized from FERNET_KEY")
            return _fernet
        except Exception:
            logger.error("Invalid FERNET_KEY format — must be a valid Fernet key")
            return None

    secret = os.getenv("JWT_SECRET", "")
    if not secret:
        logger.warning("Neither FERNET_KEY nor JWT_SECRET set — encryption disabled")
        return None

    logger.warning(
        "Using JWT_SECRET-derived Fernet key (deprecated). "
        "Set FERNET_KEY for independent key rotation."
    )
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
