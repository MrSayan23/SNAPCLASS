import bcrypt


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with salt.
    
    Usage:
        hashed = hash_password(user_password)
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def check_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored bcrypt hash (with fallback for legacy plaintext).
    
    Usage:
        if check_password(entered_password, stored_hash):
            # login success
    """
    try:
        if stored_hash and (
            stored_hash.startswith("$2a$")
            or stored_hash.startswith("$2b$")
            or stored_hash.startswith("$2y$")
        ):
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        # Fallback for unhashed legacy test passwords
        return password == stored_hash
    except Exception:
        return False
