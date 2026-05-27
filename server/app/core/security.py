from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

ALGORITHM = "HS256"
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional auth — returns None if no token provided."""
    if not credentials:
        return None
    try:
        return decode_token(credentials.credentials)
    except Exception:
        return None
