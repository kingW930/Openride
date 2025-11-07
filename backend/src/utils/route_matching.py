"""
AI-powered route matching utilities for OpenRide

This module implements an intelligent route matching algorithm that considers:
1. Location similarity (exact match, same area, adjacent areas, same region)
2. Time compatibility (departure time alignment)
3. Route efficiency (pickup location on direct path)
4. Availability bonuses (seats available, driver rating, verification status)

Future ML Enhancements:
- Integrate TensorFlow.js for learning from user booking preferences
- Implement collaborative filtering based on successful bookings
- Track user behavior patterns to improve recommendations
- Use historical data to predict optimal routes
"""
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta

# Import location utilities
from .location_utils import (
    LOCATION_COORDINATES,
    LOCATION_GROUPS,
    ADJACENT_AREAS,
    calculate_distance,
    calculate_location_similarity
)


def calculate_time_compatibility(
    search_time: str,
    route_departure_time: str,
    time_range: Optional[str] = None
) -> Tuple[float, List[str]]:
    """
    Calculate time compatibility score (0-100) with reasoning
    
    Scoring:
    - Within 15 minutes: 100 points
    - Within 30 minutes: 80 points
    - Within 1 hour: 60 points
    - Within 2 hours: 40 points
    
    Args:
        search_time: User's preferred departure time (HH:MM format)
        route_departure_time: Route's departure time (HH:MM format)
        time_range: Optional time range (e.g., "06:00-08:00")
    
    Returns:
        Tuple of (score, reasons)
    """
    reasons = []
    
    # Parse times
    def time_to_minutes(time_str: str) -> int:
        """Convert HH:MM to minutes since midnight"""
        try:
            hours, minutes = map(int, time_str.split(":"))
            return hours * 60 + minutes
        except:
            return 0
    
    route_minutes = time_to_minutes(route_departure_time)
    
    # If time_range provided, use the start of range, otherwise use search_time
    if time_range and "-" in time_range:
        start_time = time_range.split("-")[0].strip()
        search_minutes = time_to_minutes(start_time)
    elif search_time:
        search_minutes = time_to_minutes(search_time)
    else:
        # No specific time preference, give neutral score
        return 50.0, ["Flexible timing"]
    
    # Calculate time difference in minutes
    time_diff = abs(route_minutes - search_minutes)
    
    # Calculate score based on time difference
    if time_diff <= 15:
        score = 100
        reasons.append(f"Perfect timing: Within 15 minutes of preferred time")
    elif time_diff <= 30:
        score = 80
        reasons.append(f"Good timing: Within 30 minutes ({time_diff} min difference)")
    elif time_diff <= 60:
        score = 60
        reasons.append(f"Acceptable timing: Within 1 hour ({time_diff} min difference)")
    elif time_diff <= 120:
        score = 40
        reasons.append(f"Moderate timing: Within 2 hours")
    else:
        score = 20
        reasons.append(f"Different time slot")
    
    return score, reasons


def calculate_route_efficiency(
    search_from: str,
    search_to: str,
    route_from: str,
    route_to: str,
    route_bus_stops: List[str]
) -> Tuple[float, List[str]]:
    """
    Calculate route efficiency score (0-100) with reasoning
    
    Checks if pickup and dropoff locations are on the direct path
    
    Scoring:
    - Both pickup and dropoff on direct path: 100 points
    - Pickup on path, dropoff close: 80 points
    - Small detour required (< 5km): 60 points
    - Moderate detour (5-10km): 40 points
    - Large detour: 20 points
    
    Args:
        search_from: User's pickup location
        search_to: User's dropoff location
        route_from: Route's start location
        route_to: Route's end location
        route_bus_stops: List of bus stops on route
    
    Returns:
        Tuple of (score, reasons)
    """
    reasons = []
    score = 0.0
    
    # Check if both locations match route exactly
    if (search_from == route_from or search_from in route_bus_stops) and \
       (search_to == route_to or search_to in route_bus_stops):
        score = 100
        reasons.append("Perfect route: Pickup and dropoff on direct path")
        return score, reasons
    
    # Check if pickup location is on route
    pickup_on_route = (search_from == route_from or search_from in route_bus_stops)
    # Check if dropoff location is on route
    dropoff_on_route = (search_to == route_to or search_to in route_bus_stops)
    
    if pickup_on_route and dropoff_on_route:
        score = 100
        reasons.append("Optimal route: Both stops on direct path")
    elif pickup_on_route:
        score = 80
        reasons.append("Good route: Pickup on path")
        # Check dropoff proximity
        if search_to in ADJACENT_AREAS.get(route_to, []):
            reasons.append(f"Dropoff close to destination")
    elif dropoff_on_route:
        score = 80
        reasons.append("Good route: Dropoff on path")
        # Check pickup proximity
        if search_from in ADJACENT_AREAS.get(route_from, []):
            reasons.append(f"Pickup close to route start")
    else:
        # Calculate if it's a reasonable detour
        # Check if locations are in adjacent areas
        pickup_adjacent = (search_from in ADJACENT_AREAS.get(route_from, []) or 
                          route_from in ADJACENT_AREAS.get(search_from, []))
        dropoff_adjacent = (search_to in ADJACENT_AREAS.get(route_to, []) or 
                           route_to in ADJACENT_AREAS.get(search_to, []))
        
        if pickup_adjacent and dropoff_adjacent:
            score = 60
            reasons.append("Minor detour required")
        elif pickup_adjacent or dropoff_adjacent:
            score = 40
            reasons.append("Moderate detour required")
        else:
            # Check distance if coordinates available
            if all(loc in LOCATION_COORDINATES for loc in [search_from, route_from, search_to, route_to]):
                pickup_distance = calculate_distance(
                    LOCATION_COORDINATES[search_from],
                    LOCATION_COORDINATES[route_from]
                )
                dropoff_distance = calculate_distance(
                    LOCATION_COORDINATES[search_to],
                    LOCATION_COORDINATES[route_to]
                )
                total_detour = pickup_distance + dropoff_distance
                
                if total_detour < 5:
                    score = 60
                    reasons.append(f"Small detour: {total_detour:.1f}km")
                elif total_detour < 10:
                    score = 40
                    reasons.append(f"Moderate detour: {total_detour:.1f}km")
                else:
                    score = 20
                    reasons.append("Significant detour required")
            else:
                score = 30
                reasons.append("Route requires some detour")
    
    return score, reasons


def calculate_availability_bonus(
    available_seats: int,
    driver_rating: float,
    is_verified: bool
) -> Tuple[float, List[str]]:
    """
    Calculate bonus points based on availability factors
    
    Bonuses:
    - More seats available (3+): +10 points
    - Driver rating > 4.5: +10 points
    - Verified driver: +5 points
    
    Args:
        available_seats: Number of available seats
        driver_rating: Driver's rating (0-5)
        is_verified: Whether driver is verified
    
    Returns:
        Tuple of (bonus_score, reasons)
    """
    reasons = []
    bonus = 0.0
    
    if available_seats >= 3:
        bonus += 10
        reasons.append(f"Multiple seats available ({available_seats})")
    elif available_seats >= 2:
        bonus += 5
        reasons.append(f"{available_seats} seats available")
    
    if driver_rating >= 4.5:
        bonus += 10
        reasons.append(f"Highly rated driver ({driver_rating:.1f}★)")
    elif driver_rating >= 4.0:
        bonus += 5
        reasons.append(f"Good driver rating ({driver_rating:.1f}★)")
    
    if is_verified:
        bonus += 5
        reasons.append("Verified driver")
    
    return bonus, reasons


def calculate_route_match(
    search_from: str,
    search_to: str,
    search_time: str,
    time_range: Optional[str],
    route: Dict
) -> Dict:
    """
    Calculate comprehensive AI match score for a route
    
    Combines multiple factors:
    1. Location similarity (from and to) - weighted 40%
    2. Time compatibility - weighted 30%
    3. Route efficiency - weighted 20%
    4. Availability bonuses - weighted 10%
    
    Total score: 0-100
    
    Args:
        search_from: User's pickup location
        search_to: User's dropoff location
        search_time: User's preferred time
        time_range: Optional time range
        route: Route object with details
    
    Returns:
        Dict with match details including:
        - matchScore: Total score (0-100)
        - breakdown: Scores for each component
        - reasons: List of reasons for the match
        - confidence: Confidence level (high/medium/low)
    
    Future ML Enhancement:
    This function can be enhanced with TensorFlow.js to learn from:
    - User booking patterns and preferences
    - Successful vs cancelled bookings
    - Time preferences by user demographics
    - Popular route combinations
    """
    all_reasons = []
    
    # 1. Calculate location similarity for pickup (20% weight)
    from_score, from_reasons = calculate_location_similarity(
        search_from,
        route.get("start_location", ""),
        route.get("bus_stops", [])
    )
    all_reasons.extend([f"📍 Pickup: {r}" for r in from_reasons])
    
    # 2. Calculate location similarity for dropoff (20% weight)
    to_score, to_reasons = calculate_location_similarity(
        search_to,
        route.get("end_location", ""),
        route.get("bus_stops", [])
    )
    all_reasons.extend([f"🎯 Dropoff: {r}" for r in to_reasons])
    
    # 3. Calculate time compatibility (30% weight)
    time_score, time_reasons = calculate_time_compatibility(
        search_time,
        route.get("departure_time", ""),
        time_range
    )
    all_reasons.extend([f"🕐 {r}" for r in time_reasons])
    
    # 4. Calculate route efficiency (20% weight)
    efficiency_score, efficiency_reasons = calculate_route_efficiency(
        search_from,
        search_to,
        route.get("start_location", ""),
        route.get("end_location", ""),
        route.get("bus_stops", [])
    )
    all_reasons.extend([f"🛣️ {r}" for r in efficiency_reasons])
    
    # 5. Calculate availability bonus (10% weight)
    bonus_score, bonus_reasons = calculate_availability_bonus(
        route.get("available_seats", 0),
        route.get("driver_rating", 0.0),
        route.get("is_verified", False) or route.get("is_verified", "") == "true"
    )
    all_reasons.extend([f"✨ {r}" for r in bonus_reasons])
    
    # Calculate weighted total score
    weighted_score = (
        (from_score * 0.20) +      # Pickup location: 20%
        (to_score * 0.20) +         # Dropoff location: 20%
        (time_score * 0.30) +       # Time: 30%
        (efficiency_score * 0.20) + # Route efficiency: 20%
        (bonus_score * 0.10)        # Bonuses: 10%
    )
    
    # Ensure score is within 0-100
    final_score = min(max(weighted_score, 0), 100)
    
    # Determine confidence level
    if final_score >= 80:
        confidence = "high"
    elif final_score >= 60:
        confidence = "medium"
    else:
        confidence = "low"
    
    return {
        "matchScore": round(final_score, 2),
        "breakdown": {
            "pickup_location": round(from_score, 2),
            "dropoff_location": round(to_score, 2),
            "time": round(time_score, 2),
            "efficiency": round(efficiency_score, 2),
            "bonus": round(bonus_score, 2)
        },
        "reasons": all_reasons,
        "confidence": confidence
    }


def rank_routes(
    routes: List[Dict],
    search_from: str,
    search_to: str,
    search_time: str = "",
    time_range: Optional[str] = None
) -> List[Dict]:
    """
    Rank and score all routes based on AI matching algorithm
    
    Args:
        routes: List of route objects
        search_from: User's pickup location
        search_to: User's dropoff location
        search_time: User's preferred departure time
        time_range: Optional time range filter
    
    Returns:
        List of routes sorted by match score (highest first) with AI match data
    
    Future Enhancement:
    Implement collaborative filtering to recommend routes based on:
    - Similar users' successful bookings
    - Popular routes for this route combination
    - Historical booking success rates
    """
    scored_routes = []
    
    for route in routes:
        # Calculate AI match score
        match_data = calculate_route_match(
            search_from,
            search_to,
            search_time,
            time_range,
            route
        )
        
        # Add match data to route
        route["aiScore"] = match_data["matchScore"]
        route["aiBreakdown"] = match_data["breakdown"]
        route["aiReasons"] = match_data["reasons"]
        route["aiConfidence"] = match_data["confidence"]
        
        scored_routes.append(route)
    
    # Sort by AI score descending
    scored_routes.sort(key=lambda x: x.get("aiScore", 0), reverse=True)
    
    return scored_routes
