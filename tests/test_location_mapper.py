"""
Unit tests for LocationMapper: Haversine distance, reliability thresholds, and IDW interpolation.
"""

from backend.location_mapper import (
    haversine_distance_km,
    evaluate_coverage_reliability,
    LocationMapper,
    DEFAULT_NEIGHBOURHOODS
)

def test_haversine_distance():
    # Distance between Connaught Place (28.6315, 77.2167) and ITO (28.6289, 77.2410) ~ 2.38 km
    dist = haversine_distance_km(28.6315, 77.2167, 28.6289, 77.2410)
    assert 2.0 <= dist <= 2.8

def test_coverage_reliability_tiers():
    assert evaluate_coverage_reliability(2.5) == "HIGH"
    assert evaluate_coverage_reliability(5.0) == "HIGH"
    assert evaluate_coverage_reliability(7.5) == "MEDIUM"
    assert evaluate_coverage_reliability(15.0) == "MEDIUM"
    assert evaluate_coverage_reliability(18.2) == "ESTIMATED"

def test_find_nearest_station():
    mapper = LocationMapper()
    # Connaught Place is very close to ITO and Mandir Marg
    station, dist, reliability = mapper.find_nearest_station(28.6315, 77.2167)
    assert station is not None
    assert dist < 5.0
    assert reliability == "HIGH"
    assert station["city"] == "Delhi"

def test_idw_estimation():
    mapper = LocationMapper()
    measurements = [
        {"station_id": "ST1", "name": "Station A", "latitude": 28.60, "longitude": 77.20, "pollutants": {"pm25": 100.0, "pm10": 200.0}},
        {"station_id": "ST2", "name": "Station B", "latitude": 28.62, "longitude": 77.22, "pollutants": {"pm25": 150.0, "pm10": 250.0}},
    ]
    # Midpoint estimation
    res = mapper.estimate_pollutants_idw(28.61, 77.21, measurements)
    assert res["provenance"] == "SPATIALLY_ESTIMATED"
    assert 110.0 <= res["values"]["pm25"] <= 140.0

