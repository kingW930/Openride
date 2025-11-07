"""
Location and distance calculation utilities for route matching

Provides geographic calculations and location grouping data for Nigerian areas
"""
from typing import Tuple, List, Dict
import math


# Nigerian major cities/areas coordinates (approximate - latitude, longitude)
LOCATION_COORDINATES = {
    # Mainland areas
    "Ogba": (6.6388, 3.3374),
    "Ikeja": (6.6018, 3.3515),
    "Surulere": (6.4969, 3.3579),
    "Yaba": (6.5159, 3.3786),
    "Festac": (6.4655, 3.2850),
    "Berger": (6.6524, 3.3538),
    "Ketu": (6.5990, 3.3886),
    "Oshodi": (6.5449, 3.3365),
    "Mushin": (6.5284, 3.3418),
    "Agege": (6.6156, 3.3139),
    
    # Island areas
    "VI": (6.4281, 3.4219),  # Victoria Island
    "Lekki": (6.4474, 3.5497),
    "Ikoyi": (6.4520, 3.4340),
    "Marina": (6.4501, 3.3958),
    "CMS": (6.4508, 3.3916),
    "Obalende": (6.4416, 3.4074),
    "Ajah": (6.4668, 3.5665),
    
    # Other areas
    "Ikorodu": (6.6194, 3.5051),
}


# Location grouping for intelligent matching
LOCATION_GROUPS = {
    "mainland": ["Ogba", "Ikeja", "Surulere", "Yaba", "Festac", "Oshodi", "Mushin", "Agege", "Berger", "Ketu"],
    "island": ["VI", "Lekki", "Ikoyi", "Marina", "CMS", "Obalende", "Ajah"],
    "western_mainland": ["Ogba", "Ikeja", "Agege", "Berger"],
    "eastern_mainland": ["Festac", "Surulere", "Yaba", "Oshodi", "Mushin"],
    "southern_island": ["VI", "Lekki", "Ajah"],
    "northern_island": ["Ikoyi", "Marina", "CMS", "Obalende"],
}


# Adjacent areas mapping (locations close to each other)
ADJACENT_AREAS = {
    "Ogba": ["Ikeja", "Agege", "Berger"],
    "Ikeja": ["Ogba", "Agege", "Oshodi", "Berger"],
    "Agege": ["Ogba", "Ikeja"],
    "Berger": ["Ogba", "Ikeja", "Ketu"],
    "Ketu": ["Berger", "Ikeja"],
    "Oshodi": ["Ikeja", "Mushin", "Surulere", "Yaba"],
    "Mushin": ["Oshodi", "Surulere", "Yaba"],
    "Surulere": ["Oshodi", "Mushin", "Yaba"],
    "Yaba": ["Surulere", "Oshodi", "Mushin"],
    "Festac": ["Oshodi"],
    "VI": ["Lekki", "Ikoyi", "Obalende"],
    "Lekki": ["VI", "Ikoyi", "Ajah"],
    "Ikoyi": ["VI", "Lekki", "Obalende", "Marina"],
    "Ajah": ["Lekki"],
    "Marina": ["CMS", "Obalende", "Ikoyi"],
    "CMS": ["Marina", "Obalende"],
    "Obalende": ["Marina", "CMS", "Ikoyi", "VI"],
    "Ikorodu": [],
}


def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    
    Args:
        coord1: Tuple of (latitude, longitude)
        coord2: Tuple of (latitude, longitude)
    
    Returns:
        Distance in kilometers
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def calculate_location_similarity(
    search_location: str,
    route_location: str,
    route_bus_stops: List[str]
) -> Tuple[float, List[str]]:
    """
    Calculate location similarity score (0-100) with reasoning
    
    Scoring:
    - Exact match: 100 points
    - Same area/district: 80 points
    - Adjacent areas: 60 points
    - Same mainland/island: 40 points
    - Geographic proximity: 20-40 points based on distance
    
    Args:
        search_location: User's search location
        route_location: Route's start/end location
        route_bus_stops: List of bus stops on the route
    
    Returns:
        Tuple of (score, reasons)
    """
    reasons = []
    score = 0.0
    
    # Check exact match
    if search_location == route_location:
        score = 100
        reasons.append(f"Exact location match: {search_location}")
        return score, reasons
    
    # Check if search location is in bus stops
    if search_location in route_bus_stops:
        score = 100
        reasons.append(f"Direct stop at {search_location}")
        return score, reasons
    
    # Check adjacent areas
    if route_location in ADJACENT_AREAS.get(search_location, []):
        score = 60
        reasons.append(f"Adjacent area: {route_location} is near {search_location}")
    elif search_location in ADJACENT_AREAS.get(route_location, []):
        score = 60
        reasons.append(f"Adjacent area: {search_location} is near {route_location}")
    
    # Check if any bus stop is adjacent
    for stop in route_bus_stops:
        if stop in ADJACENT_AREAS.get(search_location, []):
            score = max(score, 60)
            if f"Adjacent area" not in " ".join(reasons):
                reasons.append(f"Route passes near {search_location} via {stop}")
            break
    
    # Check same district/group
    if score < 60:
        for group_name, locations in LOCATION_GROUPS.items():
            if search_location in locations and route_location in locations:
                score = max(score, 80)
                reasons.append(f"Same area: Both in {group_name.replace('_', ' ')}")
                break
    
    # Check same mainland/island
    if score < 60:
        search_in_mainland = search_location in LOCATION_GROUPS["mainland"]
        route_in_mainland = route_location in LOCATION_GROUPS["mainland"]
        search_in_island = search_location in LOCATION_GROUPS["island"]
        route_in_island = route_location in LOCATION_GROUPS["island"]
        
        if (search_in_mainland and route_in_mainland) or (search_in_island and route_in_island):
            score = max(score, 40)
            region = "mainland" if search_in_mainland else "island"
            reasons.append(f"Same region: Both on {region}")
    
    # Calculate geographic proximity if locations have coordinates
    if search_location in LOCATION_COORDINATES and route_location in LOCATION_COORDINATES:
        distance = calculate_distance(
            LOCATION_COORDINATES[search_location],
            LOCATION_COORDINATES[route_location]
        )
        
        if distance < 5 and score < 60:
            score = max(score, 40)
            reasons.append(f"Close proximity: {distance:.1f}km away")
        elif distance < 10 and score < 40:
            score = max(score, 20)
            reasons.append(f"Nearby location: {distance:.1f}km away")
    
    # Default minimal score if in same city
    if score == 0:
        score = 10
        reasons.append("Same city area")
    
    return score, reasons
