from pwdlib import PasswordHash

hashed_hasdher = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    """hash plain password"""
    return hashed_hasdher.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verify plain password with hashed password"""
    return hashed_hasdher.verify(plain_password, hashed_password)
