import base64
from cryptography.fernet import Fernet

SECRET_KEY_FALLBACK = "opspilot-fallback-cryptographic-signing-key-32-chars"

# Ensure we have a valid 32-byte Fernet key base64-encoded
key_bytes = SECRET_KEY_FALLBACK.encode()[:32].rjust(32, b'0')
fernet_key = base64.urlsafe_b64encode(key_bytes)
cipher_suite = Fernet(fernet_key)

def encrypt_token(token: str) -> str:
    """
    Encrypts a plaintext Git OAuth / Deploy Token.
    """
    if not token:
        return ""
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypts a ciphertext Git OAuth / Deploy Token.
    """
    if not encrypted_token:
        return ""
    return cipher_suite.decrypt(encrypted_token.encode()).decode()
