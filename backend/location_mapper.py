"""
Location mapping and spatial proximity estimation system.
Calculates distance to official CPCB CAAQMS stations using the Haversine formula,
evaluates spatial coverage reliability, and performs Inverse Distance Weighting (IDW).
"""

import math
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from backend.config import DATA_DIR, PROVENANCE_DIRECT, PROVENANCE_ESTIMATED

EARTH_RADIUS_KM = 6371.0

# Pre-defined major urban neighbourhoods for Diwali analysis
DEFAULT_NEIGHBOURHOODS = [
    {
        "name": "Connaught Place, Central Delhi",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.6315,
        "longitude": 77.2167,
        "description": "High commercial & pedestrian density; central business district."
    },
    {
        "name": "Karol Bagh, Central-West Delhi",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.6514,
        "longitude": 77.1907,
        "description": "Dense mixed commercial and residential market zone."
    },
    {
        "name": "Saket, South Delhi",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.5244,
        "longitude": 77.2066,
        "description": "Residential, retail malls, and hospital zone."
    },
    {
        "name": "Dwarka Sector 10, South-West Delhi",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.5823,
        "longitude": 77.0500,
        "description": "High-density residential sub-city close to IGI Airport."
    },
    {
        "name": "Rohini Sector 15, North-West Delhi",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.7180,
        "longitude": 77.1280,
        "description": "Dense residential and institutional cluster."
    },
    {
        "name": "Lajpat Nagar, South Delhi",
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.5700,
        "longitude": 77.2400,
        "description": "Dense shopping and residential neighbourhood."
    },
    {
        "name": "Sector 18, Noida",
        "city": "Noida",
        "state": "Uttar Pradesh",
        "latitude": 28.5708,
        "longitude": 77.3260,
        "description": "Key commercial hub adjacent to Delhi-UP border."
    },
    {
        "name": "Cyber City, DLF Phase 2, Gurugram",
        "city": "Gurugram",
        "state": "Haryana",
        "latitude": 28.4950,
        "longitude": 77.0890,
        "description": "Major corporate IT tech park and transit highway."
    },
    {
        "name": "Indirapuram, Ghaziabad",
        "city": "Ghaziabad",
        "state": "Uttar Pradesh",
        "latitude": 28.6415,
        "longitude": 77.3712,
        "description": "Dense suburban residential township in NCR."
    },
    {
        "name": "Bandra Kurla Complex (BKC), Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.0657,
        "longitude": 72.8687,
        "description": "Premier international financial centre and commercial complex."
    },
    {
        "name": "Koramangala, Bengaluru",
        "city": "Bengaluru",
        "state": "Karnataka",
        "latitude": 12.9352,
        "longitude": 77.6245,
        "description": "Major tech corridor and commercial-residential hub."
    }
]

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two GPS coordinates in kilometers.
    Formula: d = 2 * R * asin(sqrt(sin^2(dlat/2) + cos(lat1)*cos(lat2)*sin^2(dlon/2)))
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(EARTH_RADIUS_KM * c, 2)

def evaluate_coverage_reliability(distance_km: float) -> str:
    """
    Assign scientific reliability tier based on distance to nearest continuous monitor:
    - HIGH (< 5.0 km): High spatial correlation; station directly represents local air shed.
    - MEDIUM (5.0 - 15.0 km): Moderate spatial correlation; influenced by regional drift.
    - ESTIMATED (> 15.0 km): Low local resolution; spatial interpolation required.
    """
    if distance_km <= 5.0:
        return "HIGH"
    elif distance_km <= 15.0:
        return "MEDIUM"
    else:
        return "ESTIMATED"

class LocationMapper:
    def __init__(self, stations_json_path: Optional[str] = None):
        if stations_json_path is None:
            stations_json_path = str(DATA_DIR / "official_cpcb_stations.json")
        
        with open(stations_json_path, "r", encoding="utf-8") as f:
            self.stations = json.load(f)

    def find_nearest_station(self, lat: float, lon: float) -> Tuple[Dict[str, Any], float, str]:
        """
        Finds the nearest official monitoring station, computes distance, and evaluates reliability.
        """
        best_station = None
        min_dist = float("inf")

        for station in self.stations:
            dist = haversine_distance_km(lat, lon, station["latitude"], station["longitude"])
            if dist < min_dist:
                min_dist = dist
                best_station = station

        reliability = evaluate_coverage_reliability(min_dist)
        return best_station, min_dist, reliability

    def get_nearby_stations(self, lat: float, lon: float, radius_km: float = 25.0) -> List[Dict[str, Any]]:
        """
        Returns all official stations within a given radius, sorted by distance.
        """
        results = []
        for station in self.stations:
            dist = haversine_distance_km(lat, lon, station["latitude"], station["longitude"])
            if dist <= radius_km:
                item = dict(station)
                item["distance_km"] = dist
                item["coverage_reliability"] = evaluate_coverage_reliability(dist)
                results.append(item)

        results.sort(key=lambda x: x["distance_km"])
        return results

    def estimate_pollutants_idw(
        self,
        target_lat: float,
        target_lon: float,
        station_measurements: List[Dict[str, Any]],
        power: float = 2.0
    ) -> Dict[str, Any]:
        """
        Perform spatial estimation using Inverse Distance Weighting (IDW).
        Interpolates PM2.5, PM10, NO2, etc. from nearby reporting official stations.
        Returns estimated values with explicit SPATIALLY_ESTIMATED provenance tags.
        """
        if not station_measurements:
            return {
                "provenance": PROVENANCE_ESTIMATED,
                "values": {},
                "note": "No active stations available for IDW estimation."
            }

        # Check if target is essentially collocated with a station (dist < 0.2 km)
        for sm in station_measurements:
            dist = haversine_distance_km(target_lat, target_lon, sm["latitude"], sm["longitude"])
            if dist < 0.2:
                return {
                    "provenance": PROVENANCE_DIRECT,
                    "nearest_station_id": sm.get("station_id"),
                    "nearest_station_name": sm.get("name"),
                    "distance_km": dist,
                    "values": sm.get("pollutants", {}),
                    "note": f"Collocated with official station {sm.get('name')}"
                }

        # Compute weights: w_i = 1 / (d_i + epsilon)^power
        epsilon = 0.3  # Prevents division by zero
        weights = []
        for sm in station_measurements:
            dist = haversine_distance_km(target_lat, target_lon, sm["latitude"], sm["longitude"])
            w = 1.0 / ((dist + epsilon) ** power)
            weights.append((w, sm, dist))

        total_weight = sum(w for w, _, _ in weights)
        estimated_pollutants: Dict[str, float] = {}
        target_pollutants = ["pm25", "pm10", "no2", "so2", "co", "o3"]

        for pol in target_pollutants:
            weighted_sum = 0.0
            valid_w = 0.0
            for w, sm, _ in weights:
                val = sm.get("pollutants", {}).get(pol)
                if val is not None and val >= 0:
                    weighted_sum += w * val
                    valid_w += w
            if valid_w > 0:
                estimated_pollutants[pol] = round(weighted_sum / valid_w, 1)

        nearest_st, min_dist = min(weights, key=lambda x: x[2])[1], min(weights, key=lambda x: x[2])[2]

        return {
            "provenance": PROVENANCE_ESTIMATED,
            "nearest_station_id": nearest_st.get("station_id"),
            "nearest_station_name": nearest_st.get("name"),
            "distance_km": round(min_dist, 2),
            "coverage_reliability": evaluate_coverage_reliability(min_dist),
            "contributing_stations_count": len(station_measurements),
            "values": estimated_pollutants,
            "methodology": f"Inverse Distance Weighting (IDW p={power}) from {len(station_measurements)} official CPCB stations."
        }

