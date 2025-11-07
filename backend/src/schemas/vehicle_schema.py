"""
Vehicle schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class VehicleBase(BaseModel):
    plate_number: str = Field(..., min_length=5, max_length=20)
    make: str = Field(..., min_length=2, max_length=100)
    model: str = Field(..., min_length=2, max_length=100)
    color: str = Field(..., min_length=2, max_length=50)
    year: Optional[int] = Field(None, ge=1990, le=2025)
    total_seats: int = Field(..., ge=1, le=7)


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    color: Optional[str] = None
    total_seats: Optional[int] = Field(None, ge=1, le=7)


class VehicleResponse(BaseModel):
    id: UUID
    user_id: UUID
    plate_number: str
    make: str
    model: str
    color: str
    year: Optional[int]
    total_seats: int
    is_verified: str
    created_at: datetime
    
    class Config:
        from_attributes = True
