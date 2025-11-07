"""
Authentication controller for user registration and login
"""
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Dict

from ..models.user import User
from ..schemas.user_schema import UserCreate, UserLogin, TokenResponse, UserResponse
from ..utils.auth import hash_password, verify_password, create_access_token
from ..middleware.error_handler import BadRequestException, UnauthorizedException
from ..config.settings import get_settings

settings = get_settings()


def register_user(user_data: UserCreate, db: Session) -> TokenResponse:
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise BadRequestException("Email already registered")
    
    # Check phone number
    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_phone:
        raise BadRequestException("Phone number already registered")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hashed_password,
        role=user_data.role,
        emergency_contact=user_data.emergency_contact
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate token
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user)
    )


def login_user(login_data: UserLogin, db: Session) -> TokenResponse:
    """
    Authenticate user and return token
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        raise UnauthorizedException("Invalid email or password")
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")
    
    # Generate token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


def get_user_profile(user_id: str, db: Session) -> UserResponse:
    """
    Get user profile by ID
    """
    from uuid import UUID
    
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    
    if not user:
        raise BadRequestException("User not found")
    
    return UserResponse.from_orm(user)
