import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """
    Розрахунок відстані між двома точками на Землі
    Повертає відстань в метрах
    """
    R = 6371000  # Радіус Землі в метрах
    
    # Конвертація в радіани
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Формула Haversine
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    
    return round(distance)