"""
Direct API Route and Business Logic Tests.
Invokes endpoint controller functions directly with SQLAlchemy Session to verify
data retrieval, CPCB AQI calculation, forecasting, and data governance responses.
"""

from backend.database import SessionLocal
from backend.main import (
    get_stations,
    get_neighbourhoods,
    get_latest_air_quality,
    get_latest_weather,
    get_latest_transport,
    predict_air_quality,
    get_data_sources_summary,
    get_ml_metrics,
    get_simulation_data,
    get_simulation_timeline,
    get_heatmap_data,
    get_prediction_curves,
    get_actionable_alerts
)
from backend.schemas import PredictionRequestSchema

def test_stations_endpoint():
    db = SessionLocal()
    try:
        stations = get_stations(db)
        assert len(stations) >= 10
        station_names = [s.name for s in stations]
        assert any("Anand Vihar" in name for name in station_names)
        assert any("R K Puram" in name for name in station_names)
    finally:
        db.close()

def test_neighbourhoods_endpoint():
    db = SessionLocal()
    try:
        neighbourhoods = get_neighbourhoods(db=db)
        assert len(neighbourhoods) >= 10
        cp = next((n for n in neighbourhoods if "Connaught Place" in n.name), None)
        assert cp is not None
        assert cp.nearest_station_id is not None
        assert cp.distance_to_nearest_km < 5.0
        assert cp.coverage_reliability == "HIGH"
    finally:
        db.close()

def test_latest_air_quality_endpoint():
    db = SessionLocal()
    try:
        obs = get_latest_air_quality(limit=10, db=db)
        assert len(obs) > 0
        first = obs[0]
        assert first.cpcb_aqi is not None
        assert first.prominent_pollutant is not None
        assert first.provenance in ("DIRECTLY_MEASURED", "HISTORICAL_GOVERNMENT_RECORD", "SPATIALLY_ESTIMATED", "OFFICIAL_CSV_IMPORT")
        assert first.freshness_status in ("LIVE", "DELAYED", "HISTORICAL")
    finally:
        db.close()

def test_weather_endpoint():
    db = SessionLocal()
    try:
        weather = get_latest_weather(db=db)
        assert len(weather) > 0
        w = weather[0]
        assert w.temperature_c is not None
        assert w.humidity_pct is not None
        assert w.wind_speed_kmh is not None
    finally:
        db.close()

def test_transport_endpoint():
    db = SessionLocal()
    try:
        transport = get_latest_transport(db=db)
        assert len(transport) > 0
        t = transport[0]
        assert t.congestion_level in ("LOW", "MODERATE", "HIGH", "SEVERE")
        assert "MoRTH" in t.source_name
    finally:
        db.close()

def test_predict_endpoint_controller():
    req = PredictionRequestSchema(
        neighbourhood_or_station="Connaught Place, Central Delhi",
        scenario="strict_ban",
        hours_ahead=12
    )
    res = predict_air_quality(req)
    assert res["target_location"] == "Connaught Place, Central Delhi"
    assert len(res["predictions"]) == 12
    assert res["scenario_applied"] == "strict_ban"
    assert res["model_mae"] > 0
    assert res["model_rmse"] > 0

def test_data_sources_summary_endpoint():
    db = SessionLocal()
    try:
        summary = get_data_sources_summary(db=db)
        assert len(summary.data_sources) == 5
        departments = [ds.department for ds in summary.data_sources]
        assert any("Central Pollution Control Board" in d for d in departments)
        assert any("National Informatics Centre" in d for d in departments)
        assert any("India Meteorological Department" in d for d in departments)
        assert any("MoEFCC" in d for d in departments)
        assert any("MoRTH" in d for d in departments)
        assert len(summary.audit_logs_recent) > 0
    finally:
        db.close()

def test_ml_metrics_endpoint():
    metrics = get_ml_metrics()
    assert "metrics" in metrics
    assert metrics["metrics"]["pm25"]["r2_score"] >= 0.85
    assert metrics["metrics"]["pm10"]["r2_score"] >= 0.85

def test_simulation_endpoint():
    data = get_simulation_data()
    assert "metadata" in data
    assert data["metadata"]["city"] == "Delhi"
    assert len(data["neighbourhoods"]) == 5
    nh_names = [n["name"] for n in data["neighbourhoods"]]
    assert "Anand Vihar" in nh_names
    assert "Connaught Place" in nh_names
    assert "Rohini" in nh_names

    # Verify Ludhiana can still be selected in the filter
    ludhiana_data = get_simulation_data(city="Ludhiana")
    assert ludhiana_data["metadata"]["city"] == "Ludhiana"
    assert "Model Town" in [n["name"] for n in ludhiana_data["neighbourhoods"]]

def test_simulation_timeline_endpoint():
    timeline = get_simulation_timeline()
    assert len(timeline) == 21 # -10 to +10 (21 calendar days)
    assert timeline[0]["day_offset"] == -10
    assert timeline[0]["date"] == "2026-10-29"
    assert timeline[10]["day_offset"] == 0 # Diwali day
    assert timeline[10]["date"] == "2026-11-08"
    assert timeline[20]["day_offset"] == 10
    assert timeline[20]["date"] == "2026-11-18"

def test_festival_config_endpoint():
    from backend.main import get_festival_configuration
    cfg = get_festival_configuration()
    assert cfg["festival_name"] == "Diwali"
    assert cfg["festival_year"] == 2026
    assert cfg["festival_date"] == "2026-11-08"
    assert cfg["timezone"] == "Asia/Kolkata"
    assert cfg["total_days"] == 21
    assert cfg["start_date"] == "2026-10-29"
    assert cfg["end_date"] == "2026-11-18"
    assert len(cfg["calendar_days"]) == 21

def test_heatmap_endpoint():
    hm = get_heatmap_data(day_offset=0, hour=20)
    assert hm["city"] == "Delhi"
    assert len(hm["markers"]) == 5
    first = hm["markers"][0]
    assert "latitude" in first
    assert "longitude" in first
    assert "aqi" in first
    assert "category_color" in first

    hm_ludhiana = get_heatmap_data(city="Ludhiana", day_offset=0, hour=20)
    assert hm_ludhiana["city"] == "Ludhiana"

def test_prediction_curves_endpoint():
    curves = get_prediction_curves(neighbourhood="Anand Vihar")
    assert len(curves) == 1
    assert curves[0]["name"] == "Anand Vihar"
    assert len(curves[0]["points"]) > 0

    curves_ludhiana = get_prediction_curves(city="Ludhiana", neighbourhood="Model Town")
    assert len(curves_ludhiana) == 1
    assert curves_ludhiana[0]["name"] == "Model Town"

def test_alerts_endpoint():
    alerts = get_actionable_alerts()
    assert len(alerts) > 0
    first = alerts[0]
    assert "severity" in first
    assert "neighbourhood" in first
    assert "explanation" in first
    assert "precaution" in first

def test_cities_endpoint_and_multi_city():
    from backend.main import get_cities, get_city_details
    cities = get_cities()
    assert len(cities) == 20
    city_names = [c["city"] for c in cities]
    # Verify primary cities
    for primary in ["Delhi", "Mumbai", "Bengaluru", "Hyderabad", "Kolkata", "Chennai", "Pune", "Ahmedabad"]:
        assert primary in city_names
    # Verify additional cities
    for additional in ["Jaipur", "Lucknow", "Ludhiana", "Chandigarh", "Bhopal", "Indore", "Surat", "Nagpur", "Patna", "Kanpur", "Kochi", "Bhubaneswar"]:
        assert additional in city_names

    # Test individual city details
    delhi_cfg = get_city_details("Delhi")
    assert delhi_cfg["city"] == "Delhi"
    assert len(delhi_cfg["neighbourhoods"]) >= 5
    assert "climate_profile" in delhi_cfg

    mumbai_cfg = get_city_details("Mumbai")
    assert mumbai_cfg["city"] == "Mumbai"
    assert mumbai_cfg["climate_profile"]["dispersion_rate"] > 15.0

    # Test heatmap data with different cities
    mumbai_hm = get_heatmap_data(city="Mumbai", day_offset=0)
    assert mumbai_hm["city"] == "Mumbai"
    assert len(mumbai_hm["markers"]) >= 5
    assert mumbai_hm["center"]["latitude"] > 18.0
