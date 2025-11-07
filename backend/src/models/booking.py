"""
Booking model for OpenRide platform
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
from ..config.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"), nullable=False, index=True)
    rider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    seats_booked = Column(Integer, nullable=False, default=1)
    total_amount = Column(Float, nullable=False)
    
    payment_status = Column(String(50), nullable=False, default="pending")
    blockchain_token = Column(String(500), nullable=True)  # Token hash for verification
    
    pickup_stop = Column(String(255), nullable=False)
    dropoff_stop = Column(String(255), nullable=False)
    
    status = Column(SQLEnum(BookingStatus), nullable=False, default=BookingStatus.PENDING, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    route = relationship("Route", back_populates="bookings")
    rider = relationship("User", back_populates="bookings", foreign_keys=[rider_id])
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Booking {self.id} - {self.seats_booked} seat(s)>"
