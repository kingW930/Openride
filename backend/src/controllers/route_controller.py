"""
Route controller for managing driver routes
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from ..models.route import Route, RouteStatus
from ..models.user import User
from ..models.vehicle import Vehicle
from ..models.booking import Booking
from ..schemas.route_schema import RouteCreate, RouteUpdate, RouteSearch, RouteResponse, RouteDetailResponse
from ..middleware.error_handler import NotFoundException, BadRequestException, ForbiddenException
from ..utils.route_matching import rank_routes, is_time_in_range, calculate_route_match


def create_route(route_data: RouteCreate, driver: User, db: Session) -> RouteResponse:
    """
    Create a new route for a driver
    """
    # Verify vehicle belongs to driver
    vehicle = db.query(Vehicle).filter(
        and_(Vehicle.id == route_data.vehicle_id, Vehicle.user_id == driver.id)
    ).first()
    
    if not vehicle:
        raise NotFoundException("Vehicle not found or doesn't belong to you")
    
    # Check available seats don't exceed vehicle capacity
    if route_data.available_seats > vehicle.total_seats:
        raise BadRequestException(f"Available seats cannot exceed vehicle capacity of {vehicle.total_seats}")
    
    # Create route
    new_route = Route(
        driver_id=driver.id,
        vehicle_id=vehicle.id,
        start_location=route_data.start_location,
        end_location=route_data.end_location,
        bus_stops=route_data.bus_stops,
        departure_time=route_data.departure_time,
        departure_date=route_data.departure_date,
        available_seats=route_data.available_seats,
        price_per_seat=route_data.price_per_seat,
        status=RouteStatus.ACTIVE
    )
    
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    
    return RouteResponse.from_orm(new_route)


def get_route_by_id(route_id: UUID, db: Session) -> RouteDetailResponse:
    """
    Get detailed route information
    """
    route = db.query(Route).filter(Route.id == route_id).first()
    
    if not route:
        raise NotFoundException("Route not found")
    
    # Get driver info
    driver = route.driver
    
    # Get vehicle info
    vehicle = route.vehicle
    vehicle_info = f"{vehicle.color} {vehicle.make} {vehicle.model} ({vehicle.plate_number})"
    
    # Calculate bookings count
    bookings_count = db.query(Booking).filter(
        and_(Booking.route_id == route_id, Booking.status == "confirmed")
    ).count()
    
    # Calculate driver rating (mock for now)
    driver_rating = 4.5  # In production, calculate from ratings table
    
    route_dict = {
        **RouteResponse.from_orm(route).dict(),
        "driver_name": driver.name,
        "driver_rating": driver_rating,
        "vehicle_info": vehicle_info,
        "bookings_count": bookings_count
    }
    
    return RouteDetailResponse(**route_dict)


def search_routes(search_params: RouteSearch, db: Session) -> List[RouteDetailResponse]:
    """
    Search for available routes with AI-powered matching
    
    Uses sophisticated matching algorithm that considers:
    1. Location similarity (exact match, same area, adjacent areas, same region)
    2. Time compatibility (within preferred time range)
    3. Route efficiency (pickup/dropoff on direct path)
    4. Availability bonuses (seats, driver rating, verification)
    
    Returns top matches sorted by AI match score
    """
    # Base query - only active routes with available seats
    query = db.query(Route).filter(
        and_(
            Route.status == RouteStatus.ACTIVE,
            Route.available_seats > 0
        )
    )
    
    # Filter by date if provided
    if search_params.date:
        query = query.filter(Route.departure_date >= search_params.date)
    else:
        # Default to today and future
        query = query.filter(Route.departure_date >= datetime.utcnow().date())
    
    routes = query.all()
    
    # Convert to list of dicts for AI ranking
    routes_list = []
    for route in routes:
        driver = route.driver
        vehicle = route.vehicle
        vehicle_info = f"{vehicle.color} {vehicle.make} {vehicle.model}"
        
        # Calculate confirmed bookings
        bookings_count = db.query(Booking).filter(
            and_(Booking.route_id == route.id, Booking.status == "confirmed")
        ).count()
        
        # Get driver rating (calculate average from ratings table in production)
        # For now, using mock rating
        driver_rating = 4.5
        
        route_dict = {
            "id": str(route.id),
            "driver_id": str(route.driver_id),
            "vehicle_id": str(route.vehicle_id),
            "start_location": route.start_location,
            "end_location": route.end_location,
            "bus_stops": route.bus_stops or [],
            "departure_time": route.departure_time,
            "departure_date": route.departure_date.isoformat(),
            "available_seats": route.available_seats,
            "price_per_seat": route.price_per_seat,
            "status": route.status.value,
            "created_at": route.created_at.isoformat(),
            "driver_name": driver.name,
            "driver_rating": driver_rating,
            "is_verified": vehicle.is_verified,
            "vehicle_info": vehicle_info,
            "bookings_count": bookings_count
        }
        
        # Filter by time range if provided
        if search_params.time_range:
            if is_time_in_range(route.departure_time, search_params.time_range):
                routes_list.append(route_dict)
        else:
            routes_list.append(route_dict)
    
    # Apply AI-powered ranking algorithm
    # This uses sophisticated matching considering location, time, efficiency, and bonuses
    ranked_routes = rank_routes(
        routes_list, 
        search_params.from_location, 
        search_params.to_location,
        search_time="",  # Can be extracted from time_range
        time_range=search_params.time_range
    )
    
    # Return top matches (limit to top 20 for performance)
    top_matches = ranked_routes[:20]
    
    # Convert back to Pydantic models
    return [RouteDetailResponse(**route) for route in top_matches]


def get_driver_routes(driver: User, db: Session) -> List[RouteDetailResponse]:
    """
    Get all routes for a specific driver
    """
    routes = db.query(Route).filter(Route.driver_id == driver.id).order_by(Route.created_at.desc()).all()
    
    result = []
    for route in routes:
        vehicle = route.vehicle
        vehicle_info = f"{vehicle.color} {vehicle.make} {vehicle.model}"
        
        bookings_count = db.query(Booking).filter(
            and_(Booking.route_id == route.id, Booking.status == "confirmed")
        ).count()
        
        route_dict = {
            **RouteResponse.from_orm(route).dict(),
            "driver_name": driver.name,
            "driver_rating": 4.5,
            "vehicle_info": vehicle_info,
            "bookings_count": bookings_count
        }
        
        result.append(RouteDetailResponse(**route_dict))
    
    return result


def update_route(route_id: UUID, route_data: RouteUpdate, driver: User, db: Session) -> RouteResponse:
    """
    Update route details
    """
    route = db.query(Route).filter(
        and_(Route.id == route_id, Route.driver_id == driver.id)
    ).first()
    
    if not route:
        raise NotFoundException("Route not found or you don't have permission to update it")
    
    # Update fields
    if route_data.available_seats is not None:
        route.available_seats = route_data.available_seats
    
    if route_data.price_per_seat is not None:
        route.price_per_seat = route_data.price_per_seat
    
    if route_data.status is not None:
        route.status = RouteStatus(route_data.status)
    
    db.commit()
    db.refresh(route)
    
    return RouteResponse.from_orm(route)


def delete_route(route_id: UUID, driver: User, db: Session) -> dict:
    """
    Delete/cancel a route
    """
    route = db.query(Route).filter(
        and_(Route.id == route_id, Route.driver_id == driver.id)
    ).first()
    
    if not route:
        raise NotFoundException("Route not found or you don't have permission to delete it")
    
    # Check if there are confirmed bookings
    confirmed_bookings = db.query(Booking).filter(
        and_(Booking.route_id == route_id, Booking.status == "confirmed")
    ).count()
    
    if confirmed_bookings > 0:
        # Don't delete, just cancel
        route.status = RouteStatus.CANCELLED
        db.commit()
        return {"message": "Route cancelled successfully", "cancelled": True}
    else:
        # No bookings, safe to delete
        db.delete(route)
        db.commit()
        return {"message": "Route deleted successfully", "deleted": True}
