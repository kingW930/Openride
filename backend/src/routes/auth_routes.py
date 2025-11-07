"""
Authentication routes
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..schemas.user_schema import UserCreate, UserLogin, TokenResponse, UserResponse
from ..controllers.auth_controller import register_user, login_user, get_user_profile
from ..middleware.auth_middleware import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user (driver or rider)
    """
    return register_user(user_data, db)


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token
    """
    return login_user(login_data, db)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user profile
    """
    return UserResponse.from_orm(current_user)


@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Get user profile by ID
    """
    return get_user_profile(user_id, db)
