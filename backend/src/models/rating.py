"""
Rating model for OpenSeat platform
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..config.database import Base


class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    rater_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    rated_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    rating = Column(Float, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rater = relationship("User", back_populates="ratings_given", foreign_keys=[rater_id])
    rated_user = relationship("User", back_populates="ratings_received", foreign_keys=[rated_user_id])
    
    def __repr__(self):
        return f"<Rating {self.rating} stars>"
