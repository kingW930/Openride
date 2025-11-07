"""
Booking schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID


class BookingBase(BaseModel):
    route_id: UUID
    seats_booked: int = Field(..., ge=1, le=7, alias="seats")
    pickup_stop: str = Field(..., min_length=2)
    dropoff_stop: str = Field(..., min_length=2)


class BookingCreate(BookingBase):
    class Config:
        populate_by_name = True


class BookingUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|confirmed|cancelled|completed)$")


class BlockchainTokenData(BaseModel):
    """Blockchain token information for booking verification"""
    tokenId: str = Field(..., description="Unique token ID (SEAT-{bookingId}-{hash})")
    bookingHash: str = Field(..., description="SHA256 hash of booking details")
    transactionHash: str = Field(..., description="Blockchain transaction hash (0x...)")
    timestamp: int = Field(..., description="Token creation timestamp (Unix time)")
    blockchainNetwork: str = Field(..., description="Blockchain network name")
    verified: bool = Field(..., description="Token verification status")
    expiresAt: int = Field(..., description="Token expiration timestamp (Unix time)")
    qrData: str = Field(..., description="JSON string for QR code generation")


class BookingVerificationResponse(BaseModel):
    """Response for booking verification endpoint"""
    booking_id: UUID
    token_id: str
    rider_name: str
    rider_phone: str
    route_info: str
    seats_booked: int
    total_amount: float
    status: str
    is_redeemed: bool
    is_expired: bool
    qr_data: str
    blockchain_token: BlockchainTokenData
    verified: bool
    message: str
    
    class Config:
        from_attributes = True


class BookingResponse(BaseModel):
    id: UUID
    route_id: UUID
    rider_id: UUID
    seats_booked: int
    total_amount: float
    payment_status: str
    blockchain_token: Optional[str]
    pickup_stop: str
    dropoff_stop: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookingWithTokenResponse(BookingResponse):
    """Booking response with full blockchain token data"""
    token_data: Optional[BlockchainTokenData] = None


class BookingDetailResponse(BookingResponse):
    driver_name: str
    driver_phone: str
    vehicle_info: str
    from_location: str
    to_location: str
    departure_time: str
    departure_date: datetime
