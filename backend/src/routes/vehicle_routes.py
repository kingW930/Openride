"""
Vehicle management routes
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..config.database import get_db
from ..schemas.vehicle_schema import VehicleCreate, VehicleUpdate, VehicleResponse
from ..controllers.vehicle_controller import (
    create_vehicle,
    get_user_vehicles,
    get_vehicle_by_id,
    update_vehicle,
    delete_vehicle
)
from ..middleware.auth_middleware import get_current_driver
from ..models.user import User

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def register_vehicle(
    vehicle_data: VehicleCreate,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Register a new vehicle (drivers only)
    """
    return create_vehicle(vehicle_data, current_driver, db)


@router.get("", response_model=List[VehicleResponse])
async def get_my_vehicles(
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Get all vehicles for the current driver
    """
    return get_user_vehicles(current_driver, db)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Get vehicle details by ID
    """
    return get_vehicle_by_id(vehicle_id, current_driver, db)


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle_details(
    vehicle_id: UUID,
    vehicle_data: VehicleUpdate,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Update vehicle information
    """
    return update_vehicle(vehicle_id, vehicle_data, current_driver, db)


@router.delete("/{vehicle_id}")
async def delete_vehicle_endpoint(
    vehicle_id: UUID,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Delete a vehicle
    """
    return delete_vehicle(vehicle_id, current_driver, db)
