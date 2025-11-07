"""
Payment model for OpenRide platform
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
from ..config.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False, unique=True, index=True)
    
    amount = Column(Float, nullable=False)
    
    transaction_ref = Column(String(255), unique=True, nullable=False, index=True)
    interswitch_ref = Column(String(255), nullable=True, index=True)
    
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, index=True)
    
    payment_method = Column(String(50), nullable=True)  # card, transfer, etc.
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    booking = relationship("Booking", back_populates="payment")
    
    def __repr__(self):
        return f"<Payment {self.transaction_ref} - {self.status}>"
