"""
Route management routes (for drivers)
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..config.database import get_db
from ..schemas.route_schema import RouteCreate, RouteUpdate, RouteResponse, RouteDetailResponse, RouteSearch
from ..controllers.route_controller import (
    create_route,
    get_route_by_id,
    search_routes,
    get_driver_routes,
    update_route,
    delete_route
)
from ..middleware.auth_middleware import get_current_driver, get_optional_user
from ..models.user import User

router = APIRouter(prefix="/api/routes", tags=["Routes"])


@router.post("", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
async def create_new_route(
    route_data: RouteCreate,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Create a new route (drivers only)
    """
    return create_route(route_data, current_driver, db)


@router.get("/search", response_model=List[RouteDetailResponse])
async def search_available_routes(
    from_location: str,
    to_location: str,
    time: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """
    Search for available routes
    Query params: from, to, time (optional)
    """
    search_params = RouteSearch(
        from_location=from_location,
        to_location=to_location,
        time_range=time
    )
    return search_routes(search_params, db)


@router.get("/my-routes", response_model=List[RouteDetailResponse])
async def get_my_routes(
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Get all routes for the current driver
    """
    return get_driver_routes(current_driver, db)


@router.get("/{route_id}", response_model=RouteDetailResponse)
async def get_route(route_id: UUID, db: Session = Depends(get_db)):
    """
    Get route details by ID
    """
    return get_route_by_id(route_id, db)


@router.patch("/{route_id}", response_model=RouteResponse)
async def update_route_details(
    route_id: UUID,
    route_data: RouteUpdate,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Update route details (drivers only)
    """
    return update_route(route_id, route_data, current_driver, db)


@router.delete("/{route_id}")
async def delete_route_endpoint(
    route_id: UUID,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Delete or cancel a route (drivers only)
    """
    return delete_route(route_id, current_driver, db)
