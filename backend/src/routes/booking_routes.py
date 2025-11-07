"""
Booking management routes
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..config.database import get_db
from ..schemas.booking_schema import (
    BookingCreate, 
    BookingUpdate, 
    BookingResponse, 
    BookingDetailResponse,
    BookingWithTokenResponse,
    BookingVerificationResponse
)
from ..controllers.booking_controller import (
    create_booking,
    get_booking_by_id,
    get_user_bookings,
    get_route_bookings,
    update_booking,
    cancel_booking,
    verify_booking_by_token,
    redeem_booking_token
)
from ..middleware.auth_middleware import get_current_user, get_current_rider, get_current_driver
from ..models.user import User

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.post("", response_model=BookingWithTokenResponse, status_code=status.HTTP_201_CREATED)
async def create_new_booking(
    booking_data: BookingCreate,
    current_rider: User = Depends(get_current_rider),
    db: Session = Depends(get_db)
):
    """
    Create a new booking with blockchain token generation (riders only)
    
    This endpoint:
    1. Creates a booking in pending status
    2. Generates blockchain verification token
    3. Returns booking details with token data for QR code display
    
    The token prevents double booking and provides cryptographic verification.
    Riders receive a QR code containing the token for driver scanning.
    """
    return create_booking(booking_data, current_rider, db)


@router.get("/user/{user_id}", response_model=List[BookingDetailResponse])
async def get_user_booking_list(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all bookings for a user
    """
    # Ensure user can only view their own bookings
    if str(current_user.id) != str(user_id):
        from ..middleware.error_handler import ForbiddenException
        raise ForbiddenException("You can only view your own bookings")
    
    return get_user_bookings(current_user, db)


@router.get("/route/{route_id}", response_model=List[BookingDetailResponse])
async def get_route_booking_list(
    route_id: UUID,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Get all bookings for a specific route (drivers only)
    """
    return get_route_bookings(route_id, current_driver, db)


@router.get("/{booking_id}", response_model=BookingDetailResponse)
async def get_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get booking details by ID
    """
    return get_booking_by_id(booking_id, current_user, db)


@router.patch("/{booking_id}", response_model=BookingResponse)
async def update_booking_status(
    booking_id: UUID,
    booking_data: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update booking status
    """
    return update_booking(booking_id, booking_data, current_user, db)


@router.delete("/{booking_id}")
async def cancel_booking_endpoint(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a booking
    """
    return cancel_booking(booking_id, current_user, db)


@router.get("/{booking_id}/verify", response_model=BookingVerificationResponse)
async def verify_booking_token_endpoint(
    booking_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Verify booking blockchain token for QR scanning
    
    This endpoint is used by drivers to verify rider tokens:
    1. Scan rider's QR code containing booking ID
    2. Verify token authenticity and expiration
    3. Check if token has been redeemed (prevents double boarding)
    4. Display rider details for boarding confirmation
    
    Security Features:
    - Token format validation (SEAT-{id}-{hash})
    - Expiration check (24 hours)
    - One-time use enforcement
    - Payment verification
    
    Returns:
    - Rider name and phone
    - Booking details (seats, amount)
    - Token verification status
    - QR data for display
    """
    return verify_booking_by_token(booking_id, db)


@router.post("/{booking_id}/redeem")
async def redeem_booking_token_endpoint(
    booking_id: UUID,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Redeem booking token after rider boards (drivers only)
    
    Called by driver after:
    1. Scanning rider's QR code
    2. Verifying token is valid
    3. Confirming rider identity
    4. Rider boarding the vehicle
    
    This marks the booking as completed and prevents token reuse.
    
    Security:
    - Driver must own the route
    - Booking must be confirmed and paid
    - Token must not be expired
    - Prevents double redemption
    
    Returns:
    - Success message
    - Rider details
    - Redemption timestamp
    """
    return redeem_booking_token(booking_id, current_driver, db)
