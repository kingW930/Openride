"""
Route schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class RouteBase(BaseModel):
    start_location: str = Field(..., alias="from", min_length=2, max_length=255)
    end_location: str = Field(..., alias="to", min_length=2, max_length=255)
    bus_stops: List[str] = Field(default=[], alias="passingStops")
    departure_time: str = Field(..., alias="departureTime", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    departure_date: datetime
    available_seats: int = Field(..., alias="availableSeats", ge=1, le=7)
    price_per_seat: float = Field(..., alias="pricePerSeat", ge=100)


class RouteCreate(RouteBase):
    vehicle_id: UUID
    
    @validator('end_location')
    def validate_locations(cls, v, values):
        if 'start_location' in values and v == values['start_location']:
            raise ValueError('Start and end locations must be different')
        return v
    
    class Config:
        populate_by_name = True


class RouteUpdate(BaseModel):
    available_seats: Optional[int] = Field(None, ge=0, le=7)
    price_per_seat: Optional[float] = Field(None, ge=100)
    status: Optional[str] = Field(None, pattern="^(active|departed|completed|cancelled)$")


class RouteSearch(BaseModel):
    from_location: str = Field(..., alias="from")
    to_location: str = Field(..., alias="to")
    time_range: Optional[str] = Field(None, alias="time")
    date: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class RouteResponse(BaseModel):
    id: UUID
    driver_id: UUID
    vehicle_id: UUID
    start_location: str
    end_location: str
    bus_stops: List[str]
    departure_time: str
    departure_date: datetime
    available_seats: int
    price_per_seat: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class RouteDetailResponse(RouteResponse):
    driver_name: str
    driver_rating: float
    vehicle_info: str
    bookings_count: int
