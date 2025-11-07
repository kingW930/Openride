"""
User model for OpenSeat platform
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
from ..config.database import Base


class UserRole(str, enum.Enum):
    DRIVER = "DRIVER"
    RIDER = "RIDER"
    BOTH = "BOTH"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.RIDER)
    profile_image = Column(String(500), nullable=True)
    is_verified = Column(String(10), default="false")
    emergency_contact = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete-orphan")
    driver_routes = relationship("Route", back_populates="driver", cascade="all, delete-orphan", foreign_keys="Route.driver_id")
    bookings = relationship("Booking", back_populates="rider", cascade="all, delete-orphan", foreign_keys="Booking.rider_id")
    ratings_given = relationship("Rating", back_populates="rater", foreign_keys="Rating.rater_id")
    ratings_received = relationship("Rating", back_populates="rated_user", foreign_keys="Rating.rated_user_id")
    
    def __repr__(self):
        return f"<User {self.email}>"
