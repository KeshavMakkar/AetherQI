"""
Unit tests for HeuristicPollutionSimulator.
Verifies formulas, boundary constraints, reproducibility, and neighbourhood modifiers.
"""

from backend.services.pollution_simulator import (
    HeuristicPollutionSimulator,
    DEMO_NEIGHBOURHOODS,
    get_aqi_category_info
)

def test_before_diwali_formula():
    sim = HeuristicPollutionSimulator()
    # AQI = Base_AQI + (Traffic_Density * 0.2)
    # Base 160, traffic 80 -> 160 + 16 = 176
    aqi = sim.calculate_before_diwali_aqi(base_aqi=160.0, traffic_density=80.0)
    assert aqi == 176.0

def test_during_diwali_formula():
    sim = HeuristicPollutionSimulator()
    # AQI = Base_AQI + 300 + (Humidity * 0.5) - (Wind_Speed * 2.5)
    # Base 200, hum 80, ws 2.0 -> 200 + 300 + 40 - 5 = 535
    peak_aqi = sim.calculate_during_diwali_aqi(base_aqi=200.0, humidity=80.0, wind_speed=2.0, is_peak_hours=True)
    assert peak_aqi == 535.0
    assert peak_aqi >= 400.0 # Extreme peak spike capability

def test_after_diwali_decay_and_baseline():
    sim = HeuristicPollutionSimulator(dispersion_rate=15.0, background_baseline=140.0)
    # 500 - (4.0 * 15.0) = 440
    decayed = sim.calculate_after_diwali_aqi(prev_day_aqi=500.0, wind_speed=4.0)
    assert decayed == 440.0

    # Test baseline limit prevents falling below 140
    very_low = sim.calculate_after_diwali_aqi(prev_day_aqi=150.0, wind_speed=10.0)
    assert very_low == 140.0

def test_neighbourhood_modifiers():
    sim = HeuristicPollutionSimulator()
    # Test default Delhi neighbourhoods
    data_delhi = sim.generate_11_day_dataset()
    nh_delhi = {n["name"]: n for n in data_delhi["neighbourhoods"]}
    assert nh_delhi["Anand Vihar"]["modifier"] == 1.25
    assert nh_delhi["Anand Vihar"]["predicted_peak_aqi"] > nh_delhi["Saket"]["predicted_peak_aqi"]

    # Test Ludhiana when selected
    data_ludhiana = sim.generate_11_day_dataset(city="Ludhiana")
    nh_ludhiana = {n["name"]: n for n in data_ludhiana["neighbourhoods"]}
    assert nh_ludhiana["Model Town"]["modifier"] == 1.15
    assert nh_ludhiana["PAU Area"]["modifier"] == 0.90
    assert nh_ludhiana["Model Town"]["predicted_peak_aqi"] > nh_ludhiana["PAU Area"]["predicted_peak_aqi"]

def test_simulation_reproducibility():
    sim1 = HeuristicPollutionSimulator(seed=42)
    data1 = sim1.generate_11_day_dataset()

    sim2 = HeuristicPollutionSimulator(seed=42)
    data2 = sim2.generate_11_day_dataset()

    # Exact deterministic reproducibility
    assert data1["neighbourhoods"][0]["records"][0]["aqi"] == data2["neighbourhoods"][0]["records"][0]["aqi"]
    assert data1["neighbourhoods"][0]["predicted_peak_aqi"] == data2["neighbourhoods"][0]["predicted_peak_aqi"]

def test_aqi_categories():
    assert get_aqi_category_info(45)["category"] == "Good"
    assert get_aqi_category_info(95)["category"] == "Satisfactory"
    assert get_aqi_category_info(180)["category"] == "Moderate"
    assert get_aqi_category_info(280)["category"] == "Poor"
    assert get_aqi_category_info(350)["category"] == "Very Poor"
    assert get_aqi_category_info(480)["category"] == "Severe"

def test_21_day_timeline_generation_and_dates():
    sim = HeuristicPollutionSimulator()
    data = sim.generate_21_day_dataset(city="Ludhiana")
    
    meta = data["metadata"]
    assert meta["festival"] == "Diwali"
    assert meta["festival_date"] == "2026-11-08"
    assert meta["start_date"] == "2026-10-29"
    assert meta["end_date"] == "2026-11-18"
    assert meta["total_days"] == 21
    assert meta["timezone"] == "Asia/Kolkata"

    first_nh = data["neighbourhoods"][0]
    # Check that records cover from -10 to +10
    offsets = sorted(list(set(r["day_offset"] for r in first_nh["records"])))
    assert len(offsets) == 21
    assert offsets[0] == -10
    assert offsets[10] == 0
    assert offsets[20] == 10

    # Verify specific calendar date mapping
    date_map = {r["day_offset"]: r["date"] for r in first_nh["records"]}
    assert date_map[-10] == "2026-10-29"
    assert date_map[0] == "2026-11-08"
    assert date_map[10] == "2026-11-18"

    # Verify 24-hour diurnal profile exists on Diwali day (day_offset == 0)
    diwali_records = [r for r in first_nh["records"] if r["day_offset"] == 0]
    assert len(diwali_records) == 24
    hours = [r["hour"] for r in diwali_records]
    assert set(hours) == set(range(24))

    # Verify peak period from 8 PM (20) to 2 AM (2)
    peak_record = max(diwali_records, key=lambda r: r["aqi"])
    assert peak_record["hour"] in (20, 21, 22, 23, 0, 1, 2)
    assert peak_record["phase"] == "diwali_peak"

def test_alerts_dates_and_timeline():
    sim = HeuristicPollutionSimulator()
    data = sim.generate_21_day_dataset(city="Delhi")
    alerts = data["alerts"]
    assert len(alerts) > 0
    
    # Check that alert dates are dynamically calculated
    offsets_present = set(a.get("day_offset") for a in alerts if "day_offset" in a)
    assert -7 in offsets_present
    assert -3 in offsets_present
    assert 0 in offsets_present
    assert 2 in offsets_present
    assert 7 in offsets_present
    assert 10 in offsets_present


