"""
Booking controller for managing ride bookings
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import json

from ..models.booking import Booking, BookingStatus
from ..models.route import Route, RouteStatus
from ..models.user import User
from ..schemas.booking_schema import (
    BookingCreate, 
    BookingUpdate, 
    BookingResponse, 
    BookingDetailResponse,
    BlockchainTokenData,
    BookingWithTokenResponse,
    BookingVerificationResponse
)
from ..middleware.error_handler import NotFoundException, BadRequestException
from ..utils.blockchain import (
    generate_booking_token,
    verify_booking_token,
    validate_token_timestamp,
    generate_qr_code_data,
    simulate_blockchain_confirmation
)


def create_booking(booking_data: BookingCreate, rider: User, db: Session) -> BookingWithTokenResponse:
    """
    Create a new booking with blockchain token generation
    
    This function:
    1. Validates route availability and seat capacity
    2. Creates pending booking in database
    3. Generates blockchain verification token
    4. Simulates blockchain confirmation
    5. Returns booking with full token data for QR code generation
    """
    # Verify route exists and is active
    route = db.query(Route).filter(
        and_(Route.id == booking_data.route_id, Route.status == RouteStatus.ACTIVE)
    ).first()
    
    if not route:
        raise NotFoundException("Route not found or not available")
    
    # Check if route has enough available seats
    if route.available_seats < booking_data.seats_booked:
        raise BadRequestException(f"Only {route.available_seats} seats available")
    
    # Check if rider is trying to book their own route
    if route.driver_id == rider.id:
        raise BadRequestException("You cannot book your own route")
    
    # Calculate total amount
    total_amount = route.price_per_seat * booking_data.seats_booked
    
    # Create booking
    new_booking = Booking(
        route_id=route.id,
        rider_id=rider.id,
        seats_booked=booking_data.seats_booked,
        total_amount=total_amount,
        pickup_stop=booking_data.pickup_stop,
        dropoff_stop=booking_data.dropoff_stop,
        status=BookingStatus.PENDING,
        payment_status="pending"
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    # Generate blockchain token with full metadata
    token_data = generate_booking_token(
        booking_id=new_booking.id,
        route_id=route.id,
        rider_id=rider.id,
        amount=total_amount
    )
    
    # Simulate blockchain confirmation (2 second delay)
    # In production, this would be actual blockchain transaction
    confirmation = simulate_blockchain_confirmation(delay_seconds=0.5)  # Reduced for demo
    
    # Store token ID in database
    new_booking.blockchain_token = token_data["tokenId"]
    db.commit()
    db.refresh(new_booking)
    
    # Build response with token data
    booking_response = BookingResponse.from_orm(new_booking)
    token_response = BlockchainTokenData(**token_data)
    
    return BookingWithTokenResponse(
        **booking_response.dict(),
        token_data=token_response
    )


def get_booking_by_id(booking_id: UUID, user: User, db: Session) -> BookingDetailResponse:
    """
    Get detailed booking information
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise NotFoundException("Booking not found")
    
    # Verify user has access to this booking
    route = booking.route
    if booking.rider_id != user.id and route.driver_id != user.id:
        raise BadRequestException("You don't have permission to view this booking")
    
    # Get route and driver info
    driver = route.driver
    vehicle = route.vehicle
    vehicle_info = f"{vehicle.color} {vehicle.make} {vehicle.model} ({vehicle.plate_number})"
    
    booking_dict = {
        **BookingResponse.from_orm(booking).dict(),
        "driver_name": driver.name,
        "driver_phone": driver.phone,
        "vehicle_info": vehicle_info,
        "from_location": route.start_location,
        "to_location": route.end_location,
        "departure_time": route.departure_time,
        "departure_date": route.departure_date
    }
    
    return BookingDetailResponse(**booking_dict)


def get_user_bookings(user: User, db: Session) -> List[BookingDetailResponse]:
    """
    Get all bookings for a user (as rider or driver)
    """
    # Get bookings as rider
    rider_bookings = db.query(Booking).filter(Booking.rider_id == user.id).all()
    
    result = []
    for booking in rider_bookings:
        route = booking.route
        driver = route.driver
        vehicle = route.vehicle
        vehicle_info = f"{vehicle.color} {vehicle.make} {vehicle.model}"
        
        booking_dict = {
            **BookingResponse.from_orm(booking).dict(),
            "driver_name": driver.name,
            "driver_phone": driver.phone,
            "vehicle_info": vehicle_info,
            "from_location": route.start_location,
            "to_location": route.end_location,
            "departure_time": route.departure_time,
            "departure_date": route.departure_date
        }
        
        result.append(BookingDetailResponse(**booking_dict))
    
    return result


def get_route_bookings(route_id: UUID, driver: User, db: Session) -> List[BookingDetailResponse]:
    """
    Get all bookings for a specific route (driver only)
    """
    # Verify route belongs to driver
    route = db.query(Route).filter(
        and_(Route.id == route_id, Route.driver_id == driver.id)
    ).first()
    
    if not route:
        raise NotFoundException("Route not found or you don't have permission")
    
    bookings = db.query(Booking).filter(Booking.route_id == route_id).all()
    
    result = []
    for booking in bookings:
        rider = booking.rider
        vehicle = route.vehicle
        vehicle_info = f"{vehicle.color} {vehicle.make} {vehicle.model}"
        
        booking_dict = {
            **BookingResponse.from_orm(booking).dict(),
            "driver_name": driver.name,
            "driver_phone": driver.phone,
            "vehicle_info": vehicle_info,
            "from_location": route.start_location,
            "to_location": route.end_location,
            "departure_time": route.departure_time,
            "departure_date": route.departure_date
        }
        
        result.append(BookingDetailResponse(**booking_dict))
    
    return result


def update_booking(booking_id: UUID, booking_data: BookingUpdate, user: User, db: Session) -> BookingResponse:
    """
    Update booking status
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise NotFoundException("Booking not found")
    
    # Verify user has permission
    route = booking.route
    if booking.rider_id != user.id and route.driver_id != user.id:
        raise BadRequestException("You don't have permission to update this booking")
    
    # Update status
    if booking_data.status:
        old_status = booking.status
        new_status = BookingStatus(booking_data.status)
        booking.status = new_status
        
        # If booking is confirmed, reduce available seats
        if new_status == BookingStatus.CONFIRMED and old_status != BookingStatus.CONFIRMED:
            route.available_seats -= booking.seats_booked
        
        # If booking is cancelled, restore available seats
        elif new_status == BookingStatus.CANCELLED and old_status == BookingStatus.CONFIRMED:
            route.available_seats += booking.seats_booked
    
    db.commit()
    db.refresh(booking)
    
    return BookingResponse.from_orm(booking)


def cancel_booking(booking_id: UUID, user: User, db: Session) -> dict:
    """
    Cancel a booking
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise NotFoundException("Booking not found")
    
    # Only rider can cancel
    if booking.rider_id != user.id:
        raise BadRequestException("Only the rider can cancel this booking")
    
    # Check if already cancelled
    if booking.status == BookingStatus.CANCELLED:
        raise BadRequestException("Booking is already cancelled")
    
    # Update status
    old_status = booking.status
    booking.status = BookingStatus.CANCELLED
    
    # Restore seats if booking was confirmed
    if old_status == BookingStatus.CONFIRMED:
        route = booking.route
        route.available_seats += booking.seats_booked
    
    db.commit()
    
    return {"message": "Booking cancelled successfully", "booking_id": str(booking_id)}


def verify_booking_by_token(booking_id: UUID, db: Session) -> BookingVerificationResponse:
    """
    Verify booking using blockchain token for driver QR scanning
    
    This endpoint is used by drivers to:
    1. Scan rider's QR code containing token ID
    2. Verify token authenticity and validity
    3. Check if token has been redeemed (prevents double boarding)
    4. Display rider information for boarding
    
    Security checks:
    - Token format validation (SEAT-{id}-{hash})
    - Token expiration (24 hours)
    - Booking ID match
    - Hash integrity verification
    - One-time use enforcement
    
    Returns:
        BookingVerificationResponse with rider details and verification status
    """
    # Get booking
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise NotFoundException("Booking not found")
    
    # Get related data
    route = booking.route
    rider = booking.rider
    vehicle = route.vehicle
    
    # Check if booking has blockchain token
    if not booking.blockchain_token:
        raise BadRequestException("This booking does not have a blockchain token")
    
    # Parse token to get data
    token_parts = booking.blockchain_token.split("-")
    if len(token_parts) < 3:
        raise BadRequestException("Invalid token format")
    
    # Check if token has been redeemed (status is completed)
    is_redeemed = booking.status == BookingStatus.COMPLETED
    
    # Check token expiration (24 hours from creation)
    token_age = datetime.utcnow() - booking.created_at
    is_expired = token_age.total_seconds() > 86400  # 24 hours
    
    # Determine verification status
    verified = not is_redeemed and not is_expired and booking.payment_status == "successful"
    
    # Generate verification message
    if is_redeemed:
        message = "Token already redeemed - rider has boarded"
    elif is_expired:
        message = "Token expired - contact support"
    elif booking.payment_status != "successful":
        message = "Payment not confirmed - cannot board"
    else:
        message = "Token valid - rider can board"
    
    # Regenerate token data for QR display
    token_data_dict = generate_booking_token(
        booking_id=booking.id,
        route_id=route.id,
        rider_id=rider.id,
        amount=booking.total_amount,
        timestamp=booking.created_at
    )
    
    # Build QR data
    qr_data = generate_qr_code_data(
        token_id=booking.blockchain_token,
        booking_id=booking.id,
        timestamp=int(booking.created_at.timestamp())
    )
    
    # Build route info string
    route_info = f"{route.start_location} to {route.end_location} - {route.departure_time}"
    
    return BookingVerificationResponse(
        booking_id=booking.id,
        token_id=booking.blockchain_token,
        rider_name=rider.name,
        rider_phone=rider.phone,
        route_info=route_info,
        seats_booked=booking.seats_booked,
        total_amount=booking.total_amount,
        status=booking.status.value,
        is_redeemed=is_redeemed,
        is_expired=is_expired,
        qr_data=qr_data,
        blockchain_token=BlockchainTokenData(**token_data_dict),
        verified=verified,
        message=message
    )


def redeem_booking_token(booking_id: UUID, driver: User, db: Session) -> dict:
    """
    Redeem a booking token after scanning QR code (driver action)
    
    This marks the booking as completed and prevents the token from being used again.
    Called by driver after successful QR scan and rider boarding.
    
    Security:
    - Verifies driver owns the route
    - Checks booking is confirmed and paid
    - Prevents double redemption
    - Validates token hasn't expired
    
    Returns:
        Success message with booking details
    """
    # Get booking
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise NotFoundException("Booking not found")
    
    # Verify driver owns this route
    route = booking.route
    if route.driver_id != driver.id:
        raise BadRequestException("You don't have permission to redeem this booking")
    
    # Check booking status
    if booking.status == BookingStatus.COMPLETED:
        raise BadRequestException("Token already redeemed")
    
    if booking.status != BookingStatus.CONFIRMED:
        raise BadRequestException("Booking must be confirmed before boarding")
    
    if booking.payment_status != "successful":
        raise BadRequestException("Payment not confirmed")
    
    # Check token expiration
    token_age = datetime.utcnow() - booking.created_at
    if token_age.total_seconds() > 86400:  # 24 hours
        raise BadRequestException("Token has expired")
    
    # Mark as completed (redeemed)
    booking.status = BookingStatus.COMPLETED
    db.commit()
    
    return {
        "message": "Booking token redeemed successfully",
        "booking_id": str(booking_id),
        "rider_name": booking.rider.name,
        "seats_booked": booking.seats_booked,
        "redeemed_at": datetime.utcnow().isoformat()
    }
