"""
Unit tests for DiwaliAirPredictor.
Verifies model loading, forecast generation, scenario modifications, and AQI compliance.
"""

from backend.ml.predictor import DiwaliAirPredictor

def test_predictor_forecast():
    predictor = DiwaliAirPredictor()
    res = predictor.predict_forecast("Connaught Place, Central Delhi", hours_ahead=6, scenario="green_crackers")
    assert res["target_location"] == "Connaught Place, Central Delhi"
    assert res["nearest_station_id"] is not None
    assert res["distance_km"] < 5.0
    assert res["coverage_reliability"] == "HIGH"
    assert len(res["predictions"]) == 6

    # Verify first prediction item
    first = res["predictions"][0]
    assert first["predicted_pm25"] > 0
    assert first["predicted_pm10"] > 0
    assert 0 <= first["predicted_cpcb_aqi"] <= 500
    assert first["provenance"] == "MODEL_PREDICTED"

def test_scenario_impact():
    predictor = DiwaliAirPredictor()
    strict = predictor.predict_forecast("Anand Vihar, Delhi - DPCC", hours_ahead=12, scenario="strict_ban")
    unrestricted = predictor.predict_forecast("Anand Vihar, Delhi - DPCC", hours_ahead=12, scenario="unrestricted")
    
    # Peak night hours should show higher PM2.5 in unrestricted than strict ban
    max_strict_pm25 = max(p["predicted_pm25"] for p in strict["predictions"])
    max_unrestricted_pm25 = max(p["predicted_pm25"] for p in unrestricted["predictions"])
    assert max_unrestricted_pm25 >= max_strict_pm25

