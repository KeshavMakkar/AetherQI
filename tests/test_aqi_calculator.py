"""
Unit tests for CPCB IND-AQI Calculator.
Verifies piecewise linear breakpoints, prominent pollutant determination,
and strict multi-pollutant minimum count requirements.
"""

import pytest
from backend.aqi_calculator import calculate_sub_index, calculate_cpcb_aqi, get_aqi_category

def test_pm25_sub_index():
    # Good bracket: 0-30 -> 0-50
    assert calculate_sub_index("PM2.5", 15.0) == 25
    assert calculate_sub_index("PM2.5", 30.0) == 50
    # Satisfactory: 30.1-60 -> 51-100
    assert calculate_sub_index("PM2.5", 45.0) == 75
    # Moderate: 60.1-90 -> 101-200
    assert calculate_sub_index("PM2.5", 75.0) == 150
    # Severe: 250+ -> 401-500
    assert calculate_sub_index("PM2.5", 375.0) == 450
    # Cap at 500
    assert calculate_sub_index("PM2.5", 650.0) == 500

def test_pm10_sub_index():
    # Good bracket: 0-50 -> 0-50
    assert calculate_sub_index("PM10", 25.0) == 25
    # Satisfactory: 50.1-100 -> 51-100
    assert calculate_sub_index("PM10", 100.0) == 100
    # Moderate: 100.1-250 -> 101-200
    assert calculate_sub_index("PM10", 175.0) == 150

def test_official_compliance_with_three_pollutants():
    # PM2.5 + PM10 + NO2 -> 3 pollutants including PM -> Compliant
    pollutants = {
        "pm25": 110.0,  # Poor (subindex ~ 267)
        "pm10": 220.0,  # Moderate (subindex ~ 180)
        "no2": 65.0,    # Satisfactory (subindex ~ 82)
    }
    result = calculate_cpcb_aqi(pollutants)
    assert result["is_official_compliant"] is True
    assert result["prominent_pollutant"] == "PM2.5"
    assert result["category"] == "Poor"
    assert result["aqi"] == 267

def test_incomplete_parameters_pm_only():
    # Only PM2.5 -> NOT compliant for official AQI as per CPCB mandate
    pollutants = {"pm25": 85.0}
    result = calculate_cpcb_aqi(pollutants)
    assert result["is_official_compliant"] is False
    assert "Incomplete for Official CPCB AQI" in result["compliance_note"]
    assert "Sub-Index Only" in result["prominent_pollutant"]

def test_insufficient_parameters_no_pm():
    # NO2 + SO2 only -> Missing PM2.5 and PM10
    pollutants = {"no2": 45.0, "so2": 30.0}
    result = calculate_cpcb_aqi(pollutants)
    assert result["is_official_compliant"] is False
    assert result["aqi"] is None
    assert "Cannot compute" in result["compliance_note"]

def test_categories():
    assert get_aqi_category(40)[0] == "Good"
    assert get_aqi_category(85)[0] == "Satisfactory"
    assert get_aqi_category(160)[0] == "Moderate"
    assert get_aqi_category(250)[0] == "Poor"
    assert get_aqi_category(360)[0] == "Very Poor"
    assert get_aqi_category(450)[0] == "Severe"
