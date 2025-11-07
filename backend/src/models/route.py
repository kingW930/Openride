"""
Route model for OpenSeat platform
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from datetime import datetime
import enum
from ..config.database import Base


class RouteStatus(str, enum.Enum):
    ACTIVE = "active"
    DEPARTED = "departed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Route(Base):
    __tablename__ = "routes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False, index=True)
    
    start_location = Column(String(255), nullable=False, index=True)
    end_location = Column(String(255), nullable=False, index=True)
    bus_stops = Column(JSON, default=list)  # List of bus stop names
    
    departure_time = Column(String(10), nullable=False)  # Format: "06:30"
    departure_date = Column(DateTime, nullable=False, index=True)
    
    available_seats = Column(Integer, nullable=False)
    price_per_seat = Column(Float, nullable=False)
    
    status = Column(SQLEnum(RouteStatus), nullable=False, default=RouteStatus.ACTIVE, index=True)
    
    # AI matching metadata
    route_coordinates = Column(JSON, nullable=True)  # Lat/lng points for route matching
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    driver = relationship("User", back_populates="driver_routes", foreign_keys=[driver_id])
    vehicle = relationship("Vehicle", back_populates="routes")
    bookings = relationship("Booking", back_populates="route", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Route {self.start_location} -> {self.end_location} at {self.departure_time}>"
