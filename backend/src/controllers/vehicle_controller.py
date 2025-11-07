"""
Vehicle controller for managing vehicles
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from uuid import UUID

from ..models.vehicle import Vehicle
from ..models.user import User
from ..schemas.vehicle_schema import VehicleCreate, VehicleUpdate, VehicleResponse
from ..middleware.error_handler import NotFoundException, BadRequestException


def create_vehicle(vehicle_data: VehicleCreate, driver: User, db: Session) -> VehicleResponse:
    """
    Register a new vehicle
    """
    # Check if plate number already exists
    existing_vehicle = db.query(Vehicle).filter(Vehicle.plate_number == vehicle_data.plate_number).first()
    if existing_vehicle:
        raise BadRequestException("Vehicle with this plate number already registered")
    
    # Create vehicle
    new_vehicle = Vehicle(
        user_id=driver.id,
        plate_number=vehicle_data.plate_number,
        make=vehicle_data.make,
        model=vehicle_data.model,
        color=vehicle_data.color,
        year=vehicle_data.year,
        total_seats=vehicle_data.total_seats
    )
    
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    
    return VehicleResponse.from_orm(new_vehicle)


def get_user_vehicles(driver: User, db: Session) -> List[VehicleResponse]:
    """
    Get all vehicles for a driver
    """
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == driver.id).all()
    return [VehicleResponse.from_orm(vehicle) for vehicle in vehicles]


def get_vehicle_by_id(vehicle_id: UUID, driver: User, db: Session) -> VehicleResponse:
    """
    Get a specific vehicle
    """
    vehicle = db.query(Vehicle).filter(
        and_(Vehicle.id == vehicle_id, Vehicle.user_id == driver.id)
    ).first()
    
    if not vehicle:
        raise NotFoundException("Vehicle not found")
    
    return VehicleResponse.from_orm(vehicle)


def update_vehicle(vehicle_id: UUID, vehicle_data: VehicleUpdate, driver: User, db: Session) -> VehicleResponse:
    """
    Update vehicle information
    """
    vehicle = db.query(Vehicle).filter(
        and_(Vehicle.id == vehicle_id, Vehicle.user_id == driver.id)
    ).first()
    
    if not vehicle:
        raise NotFoundException("Vehicle not found")
    
    # Update fields
    if vehicle_data.color:
        vehicle.color = vehicle_data.color
    
    if vehicle_data.total_seats:
        vehicle.total_seats = vehicle_data.total_seats
    
    db.commit()
    db.refresh(vehicle)
    
    return VehicleResponse.from_orm(vehicle)


def delete_vehicle(vehicle_id: UUID, driver: User, db: Session) -> dict:
    """
    Delete a vehicle
    """
    vehicle = db.query(Vehicle).filter(
        and_(Vehicle.id == vehicle_id, Vehicle.user_id == driver.id)
    ).first()
    
    if not vehicle:
        raise NotFoundException("Vehicle not found")
    
    # Check if vehicle has active routes
    from ..models.route import Route, RouteStatus
    active_routes = db.query(Route).filter(
        and_(Route.vehicle_id == vehicle_id, Route.status == RouteStatus.ACTIVE)
    ).count()
    
    if active_routes > 0:
        raise BadRequestException("Cannot delete vehicle with active routes")
    
    db.delete(vehicle)
    db.commit()
    
    return {"message": "Vehicle deleted successfully"}
