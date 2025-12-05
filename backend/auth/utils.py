from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
import hashlib
from dotenv import load_dotenv

from database import get_db
from models import User
from auth.schemas import TokenData

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
# Optionally you can use a separate secret for refresh tokens:
# REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", SECRET_KEY)
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme (you can swap to OAuth2PasswordBearer if you prefer)
security = HTTPBearer()


def _prepare_password(password: str) -> str:
    """
    Pre-hash the plain password using SHA-256 and return the hex digest.
    Using hex digest produces a predictable ASCII string (64 chars) which
    is safe to pass into bcrypt (72-byte limit).
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a stored bcrypt hash.

    The stored hash is expected to be bcrypt(sha256_hexdigest(password)).
    """
    try:
        prepared_password = _prepare_password(plain_password)
        return pwd_context.verify(prepared_password, hashed_password)
    except Exception as e:
        print(f"The Error is {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password by first pre-hashing with SHA-256 (hex digest) then bcrypt.
    Store the resulting bcrypt hash in the database.
    """
    prepared_password = _prepare_password(password)
    return pwd_context.hash(prepared_password)


def _ensure_subject_in_payload(data: dict) -> str:
    """
    Helper: ensure there is a 'sub' (subject) in the payload.
    Accepts common alternatives like 'email' or 'username' and returns the subject.
    Raises ValueError if subject cannot be derived.
    """
    sub = data.get("sub") or data.get("email") or data.get("username")
    if not sub:
        raise ValueError(
            "Token payload must include 'sub' (subject) or 'email'/'username' key."
        )
    return str(sub)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token. The provided `data` must include 'sub' (or 'email'/'username').
    """
    to_encode = data.copy()
    # ensure there is a subject claim
    sub = _ensure_subject_in_payload(to_encode)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access", "sub": sub})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token. The provided `data` must include 'sub' (or 'email'/'username').
    """
    to_encode = data.copy()
    sub = _ensure_subject_in_payload(to_encode)

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh", "sub": sub})
    # If you want separate secret for refresh tokens, swap SECRET_KEY with REFRESH_SECRET_KEY here.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> TokenData:
    """
    Verify and decode a JWT token and return TokenData containing the subject (email).
    Raises HTTPException(401) on invalid or expired tokens.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        token_type_claim: Optional[str] = payload.get("type")

        if email is None or token_type_claim != token_type:
            raise credentials_exception

        return TokenData(email=email)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency to fetch the current user based on the provided access token.
    """
    token = credentials.credentials
    token_data = verify_token(token, token_type="access")

    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate user by email and password. Returns the User if successful, else None.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user