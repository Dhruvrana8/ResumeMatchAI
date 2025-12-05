from exceptions import UserAlreadyExistError
from exceptions import UserNotFoundError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from models import User
from auth.schemas import UserCreate, UserLogin, Token, UserResponse
from auth.utils import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters with at least one letter and one digit
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise UserAlreadyExistError()
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access and refresh tokens.
    
    - **email**: User's email address
    - **password**: User's password
    """
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise UserNotFoundError()
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using a valid refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    # Verify refresh token
    token_data = verify_token(refresh_token, token_type="refresh")
    
    # Get user
    user = db.query(User).filter(User.email == token_data.email).first()
    if not user:
        raise UserNotFoundError()
    
    # Create new tokens
    new_access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    
    Requires valid access token in Authorization header.
    """
    return current_user

@router.post("/logout")
async def logout():
    """
    Logout user (client should remove tokens).
    
    Since we're using JWT tokens, actual logout is handled client-side
    by removing the stored tokens.
    """
    return {"message": "Successfully logged out"}
