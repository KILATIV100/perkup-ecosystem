"""Geolocation utilities"""

import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """
    Calculate the distance between two points on Earth using the Haversine formula.

    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees

    Returns:
        Distance in meters
    """
    # Earth's radius in meters
    R = 6371000

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2 +
        math.cos(lat1_rad) * math.cos(lat2_rad) *
        math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in meters
    distance = R * c

    return round(distance)


def is_within_radius(
    user_lat: float,
    user_lon: float,
    location_lat: float,
    location_lon: float,
    radius_meters: int
) -> tuple[bool, int]:
    """
    Check if user is within radius of a location.

    Args:
        user_lat: User's latitude
        user_lon: User's longitude
        location_lat: Location's latitude
        location_lon: Location's longitude
        radius_meters: Allowed radius in meters

    Returns:
        Tuple of (is_within_radius, distance_in_meters)
    """
    distance = haversine_distance(user_lat, user_lon, location_lat, location_lon)
    return (distance <= radius_meters, distance)
