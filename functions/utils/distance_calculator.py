import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth's surface.

    Args:
        lat1 (float): Latitude of the first point.
        lon1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lon2 (float): Longitude of the second point.

    Returns:
        float: Distance between the two points in meters.
    """
    # Radius of the Earth in meters
    R = 6371000

    # Convert latitude and longitude from degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in meters
    distance = R * c

    return distance


def is_within_500_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> bool:
    """
    Check if the distance between two coordinates is less than 500 meters.

    Args:
        lat1 (float): Latitude of the first point.
        lon1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lon2 (float): Longitude of the second point.

    Returns:
        bool: True if the distance is less than 500 meters, False otherwise.
    """
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    return distance < 500

# Example usage
# lat1, lon1 = 37.7749, -122.4194  # Coordinates of San Francisco
# lat2, lon2 = 37.7750, -122.4195  # Coordinates very close to the first point

# if is_within_500_meters(lat1, lon1, lat2, lon2):
#     print("The two points are within 500 meters of each other.")
# else:
#     print("The two points are more than 500 meters apart.")
