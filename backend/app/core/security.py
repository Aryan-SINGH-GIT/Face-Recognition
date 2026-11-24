import os
import datetime
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db

SECRET_KEY = os.getenv("JWT_SECRET", "face-recognition-enterprise-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

# Use pbkdf2_sha256 which is standard hashlib compatible
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security_bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hashes a plain text password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None) -> str:
    """Encodes a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def is_token_revoked(token_str: str, db: Session) -> bool:
    """Checks whether a token has been added to the blacklist."""
    from app.db.models import RevokedToken
    return db.query(RevokedToken).filter(RevokedToken.token == token_str).first() is not None

def revoke_token(token_str: str, expires_at: datetime.datetime, db: Session):
    """Blacklists a token so it cannot be used again."""
    from app.db.models import RevokedToken
    if not is_token_revoked(token_str, db):
        revoked = RevokedToken(token=token_str, expires_at=expires_at)
        db.add(revoked)
        db.commit()

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Security(security_bearer),
    db: Session = Depends(get_db)
) -> dict:
    """
    FastAPI dependency verifying JWT bearer token for admin routes:
    - Validates signature and expiry
    - Checks server-side token blacklist
    - Returns admin payload dict (username, role, token)
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_str = credentials.credentials
    if is_token_revoked(token_str, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been logged out. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username, "role": payload.get("role", "ADMIN"), "token": token_str, "exp": payload.get("exp")}
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_optional_admin(
    credentials: HTTPAuthorizationCredentials = Security(security_bearer),
    db: Session = Depends(get_db)
) -> dict | None:
    """Returns admin payload if valid credentials provided, or None."""
    if not credentials:
        return None
    try:
        return get_current_admin(credentials, db)
    except HTTPException:
        return None
