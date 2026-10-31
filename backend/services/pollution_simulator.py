"""
AetherQI Heuristic Pollution Simulation Engine.
Demonstration simulation engine for multi-city air quality forecasting and scenario analysis.

Configured for 21 Calendar Days (T-10 to T+10):
- Festival: Diwali (Lakshmi Puja)
- Configured Date: 8 November 2026 (2026-11-08)
- Timeline Range: 29 October 2026 to 18 November 2026 (21 days)
- Timezone: Asia/Kolkata

DISCLAIMER:
This is a heuristic demonstration engine, not a scientifically validated regulatory model.
All outputs are strictly classified as "Simulated Prediction".
Supports: Ludhiana, Delhi, Chandigarh with location-isolated datasets.
"""

import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.config.festival_config import (
    FESTIVAL_NAME,
    FESTIVAL_YEAR,
    FESTIVAL_DATE_STR,
    TIMEZONE,
    TIMELINE_DAYS_BEFORE,
    TIMELINE_DAYS_AFTER,
    TOTAL_TIMELINE_DAYS,
    START_DATE_STR,
    END_DATE_STR,
    get_festival_date,
    get_festival_config
)

from backend.config.cities_config import (
    CITIES_REGISTRY,
    get_city_config,
    get_all_cities_list
)

# Supported Cities Metadata & Verified Neighbourhoods (Scaled to 20 Major Indian Metropolitan Cities)
SUPPORTED_CITIES: Dict[str, Dict[str, Any]] = CITIES_REGISTRY

# Backwards compatibility reference for Ludhiana
DEMO_NEIGHBOURHOODS = SUPPORTED_CITIES["Ludhiana"]["neighbourhoods"]

# AQI Category Thresholds (CPCB IND-AQI Standard)
def get_aqi_category_info(aqi: float) -> Dict[str, str]:
    if aqi <= 50:
        return {"category": "Good", "color": "#10B981", "badge_class": "aqi-good"}
    elif aqi <= 100:
        return {"category": "Satisfactory", "color": "#84CC16", "badge_class": "aqi-satisfactory"}
    elif aqi <= 200:
        return {"category": "Moderate", "color": "#EAB308", "badge_class": "aqi-moderate"}
    elif aqi <= 300:
        return {"category": "Poor", "color": "#F97316", "badge_class": "aqi-poor"}
    elif aqi <= 400:
        return {"category": "Very Poor", "color": "#EF4444", "badge_class": "aqi-very-poor"}
    else:
        return {"category": "Severe", "color": "#991B1B", "badge_class": "aqi-severe"}

class HeuristicPollutionSimulator:
    """
    Generates deterministic, reproducible heuristic pollution trajectories
    for the 21-day Diwali festival window (T-10 to T+10) across supported cities.
    Centralized date: 8 November 2026.
    """

    def __init__(
        self,
        base_diwali_date: Optional[datetime] = None,
        dispersion_rate: float = 14.0,
        background_baseline: float = 140.0,
        seed: int = 42
    ):
        self.dispersion_rate = dispersion_rate
        self.background_baseline = background_baseline
        self.seed = seed
        if base_diwali_date is not None:
            self.diwali_date = base_diwali_date
        else:
            self.diwali_date = get_festival_date()
        self.days_before = TIMELINE_DAYS_BEFORE
        self.days_after = TIMELINE_DAYS_AFTER

    def calculate_before_diwali_aqi(self, base_aqi: float, traffic_density: float) -> float:
        """
        Formula A: Before Diwali (T - 10 to T - 1)
        AQI = Base_AQI + (Traffic_Density * 0.2)
        Base AQI between 150 and 200, Traffic Density 0-100.
        """
        return base_aqi + (traffic_density * 0.2)

    def calculate_during_diwali_aqi(
        self,
        base_aqi: float,
        humidity: float,
        wind_speed: float,
        is_peak_hours: bool = True
    ) -> float:
        """
        Formula B: During Diwali (Peak: 8 PM - 2 AM)
        AQI = Base_AQI + 300 + (Humidity * 0.5) - (Wind_Speed * 2.5)
        Peak spike capable of reaching 400-600+.
        """
        if is_peak_hours:
            peak_spike = 300.0 + (humidity * 0.5) - (wind_speed * 2.5)
            return max(base_aqi + 150.0, base_aqi + peak_spike)
        else:
            daytime_spike = 80.0 + (humidity * 0.2) - (wind_speed * 1.5)
            return base_aqi + daytime_spike

    def calculate_after_diwali_aqi(self, prev_day_aqi: float, wind_speed: float, dispersion_rate: Optional[float] = None) -> float:
        """
        Formula C: After Diwali (T + 1 to T + 10)
        AQI_today = Previous_Day_AQI - (Wind_Speed * Dispersion_Rate)
        Gradual decline, no negative, min background baseline.
        """
        rate = dispersion_rate if dispersion_rate is not None else self.dispersion_rate
        decayed = prev_day_aqi - (wind_speed * rate)
        return max(self.background_baseline, decayed)

    def generate_21_day_dataset(self, city: str = "Delhi") -> Dict[str, Any]:
        """
        Produces the full 21-day multi-neighbourhood dataset (T-10 to T+10) for the requested city.
        Calendar range: 2026-10-29 to 2026-11-18 (21 calendar days).
        """
        city_key = "Delhi"
        for key in SUPPORTED_CITIES:
            if key.lower() == (city or "Delhi").lower():
                city_key = key
                break

        city_info = SUPPORTED_CITIES[city_key]
        city_seed = self.seed + (hash(city_key) % 1000)
        rng = random.Random(city_seed)

        start_date = self.diwali_date - timedelta(days=self.days_before)
        end_date = self.diwali_date + timedelta(days=self.days_after)

        # Baseline offset adjustments per city geography and climate profile
        climate = city_info.get("climate_profile", {})
        cfg = {
            "base_adj": climate.get("base_adj", 0.0),
            "diwali_spike_adj": climate.get("diwali_spike_adj", 0.0),
            "temp_mean": climate.get("base_temp", city_info.get("base_temp", 24.0)),
            "dispersion_rate": climate.get("dispersion_rate", self.dispersion_rate),
        }

        # Weather & traffic trajectory over all 21 calendar days (-10 to +10)
        daily_weather = {}
        for day_offset in range(-self.days_before, self.days_after + 1):
            if day_offset < -5:
                # Early Pre-Diwali Baseline (T-10 to T-6)
                base_ws = rng.uniform(4.5, 6.8)
                base_hum = rng.uniform(52.0, 62.0)
                traffic = rng.uniform(62.0, 76.0)
            elif -5 <= day_offset < 0:
                # Active Pre-Diwali Festive Shopping & Congestion (T-5 to T-1)
                base_ws = rng.uniform(3.5, 5.2)
                base_hum = rng.uniform(60.0, 72.0)
                traffic = rng.uniform(78.0, 96.0)
            elif day_offset == 0:
                # Diwali Festival Night (Peak Fireworks & Inversion)
                base_ws = rng.uniform(1.8, 2.8)
                base_hum = rng.uniform(74.0, 86.0)
                traffic = rng.uniform(65.0, 85.0)
            elif 1 <= day_offset <= 4:
                # Immediate Post-Diwali Smog Stagnation (T+1 to T+4)
                base_ws = rng.uniform(2.8, 4.2)
                base_hum = rng.uniform(68.0, 78.0)
                traffic = rng.uniform(58.0, 74.0)
            else:
                # Extended Atmospheric Recovery & Dispersion (T+5 to T+10)
                base_ws = rng.uniform(4.0, 6.2)
                base_hum = rng.uniform(55.0, 68.0)
                traffic = rng.uniform(55.0, 72.0)

            daily_weather[day_offset] = {
                "wind_speed": round(base_ws, 1),
                "humidity": round(base_hum, 1),
                "traffic_density": round(traffic, 1),
                "temperature": round(cfg["temp_mean"] + rng.uniform(-2.2, 2.2), 1)
            }

        # Baseline AQI sequence across 21 days
        baseline_trajectory = {}

        # 1. Before Diwali (T-10 to T-1)
        for d in range(-self.days_before, 0):
            w = daily_weather[d]
            # Natural gradual rise approaching Diwali due to seasonal cooling & market buildup
            approach_climb = (10 + d) * 2.2
            raw_base = rng.uniform(150.0, 168.0) + cfg["base_adj"] + approach_climb
            baseline_trajectory[d] = round(self.calculate_before_diwali_aqi(raw_base, w["traffic_density"]), 1)

        # 2. During Diwali (T, Day 0)
        w_diwali = daily_weather[0]
        diwali_base_day = 220.0 + cfg["base_adj"] + cfg["diwali_spike_adj"]
        diwali_base_peak = self.calculate_during_diwali_aqi(
            diwali_base_day,
            w_diwali["humidity"],
            w_diwali["wind_speed"],
            is_peak_hours=True
        )
        baseline_trajectory[0] = round(diwali_base_peak, 1)

        # 3. After Diwali (T+1 to T+10) - Gradual Dispersion
        prev_aqi = diwali_base_peak
        for d in range(1, self.days_after + 1):
            w = daily_weather[d]
            decayed = self.calculate_after_diwali_aqi(prev_aqi, w["wind_speed"], cfg.get("dispersion_rate"))
            baseline_trajectory[d] = round(decayed, 1)
            prev_aqi = decayed

        # Generate Neighbourhood Records
        neighbourhood_data = []
        for nh in city_info["neighbourhoods"]:
            nh_records = []
            modifier = nh["modifier"]

            for day_offset in range(-self.days_before, self.days_after + 1):
                target_date = self.diwali_date + timedelta(days=day_offset)
                date_str = target_date.strftime("%Y-%m-%d")
                w = daily_weather[day_offset]
                base_aqi = baseline_trajectory[day_offset]

                if day_offset == 0:
                    # 24-hour diurnal profile on Diwali Day
                    for hour in range(24):
                        is_peak = (20 <= hour <= 23) or (0 <= hour <= 2)
                        if is_peak:
                            hour_spike_factor = 1.0 + 0.15 * math.sin((hour - 20) * math.pi / 6)
                            raw_val = (base_aqi * hour_spike_factor) + rng.uniform(-10.0, 15.0)
                            phase = "diwali_peak"
                        elif 12 <= hour < 20:
                            raw_val = (base_aqi * 0.65) + rng.uniform(-10.0, 10.0)
                            phase = "diwali_daytime"
                        else:
                            raw_val = (base_aqi * 0.85) + rng.uniform(-15.0, 10.0)
                            phase = "diwali_morning"

                        nh_aqi = round(raw_val * modifier, 1)
                        pm25_val = round(nh_aqi * 0.48, 1)
                        pm10_val = round(nh_aqi * 0.72, 1)
                        cat_info = get_aqi_category_info(nh_aqi)

                        nh_records.append({
                            "location_id": nh["id"],
                            "city": city_key,
                            "neighbourhood": nh["name"],
                            "latitude": nh["latitude"],
                            "longitude": nh["longitude"],
                            "date": date_str,
                            "day_offset": day_offset,
                            "hour": hour,
                            "timestamp": f"{date_str}T{hour:02d}:00:00",
                            "aqi": nh_aqi,
                            "AQI": nh_aqi,
                            "pm25": pm25_val,
                            "PM2.5": pm25_val,
                            "pm10": pm10_val,
                            "PM10": pm10_val,
                            "temperature": w["temperature"],
                            "humidity": w["humidity"],
                            "wind_speed": w["wind_speed"],
                            "traffic_density": w["traffic_density"],
                            "phase": phase,
                            "category": cat_info["category"],
                            "category_color": cat_info["color"],
                            "data_source": "AetherQI Heuristic Simulation Engine",
                            "data_type": "simulated",
                            "provenance": "SIMULATED_PREDICTION"
                        })
                else:
                    phase = "pre_diwali" if day_offset < 0 else "post_diwali"
                    nh_aqi = round(base_aqi * modifier, 1)
                    pm25_val = round(nh_aqi * 0.44, 1)
                    pm10_val = round(nh_aqi * 0.68, 1)
                    cat_info = get_aqi_category_info(nh_aqi)

                    nh_records.append({
                        "location_id": nh["id"],
                        "city": city_key,
                        "neighbourhood": nh["name"],
                        "latitude": nh["latitude"],
                        "longitude": nh["longitude"],
                        "date": date_str,
                        "day_offset": day_offset,
                        "hour": 20,
                        "timestamp": f"{date_str}T20:00:00",
                        "aqi": nh_aqi,
                        "AQI": nh_aqi,
                        "pm25": pm25_val,
                        "PM2.5": pm25_val,
                        "pm10": pm10_val,
                        "PM10": pm10_val,
                        "temperature": w["temperature"],
                        "humidity": w["humidity"],
                        "wind_speed": w["wind_speed"],
                        "traffic_density": w["traffic_density"],
                        "phase": phase,
                        "category": cat_info["category"],
                        "category_color": cat_info["color"],
                        "data_source": "AetherQI Heuristic Simulation Engine",
                        "data_type": "simulated",
                        "provenance": "SIMULATED_PREDICTION"
                    })

            peak_record = max(nh_records, key=lambda r: r["aqi"])

            neighbourhood_data.append({
                "id": nh["id"],
                "name": nh["name"],
                "city": city_key,
                "state": nh["state"],
                "type": nh["type"],
                "modifier": nh["modifier"],
                "latitude": nh["latitude"],
                "longitude": nh["longitude"],
                "description": nh["description"],
                "current_aqi": nh_records[0]["aqi"],
                "predicted_peak_aqi": peak_record["aqi"],
                "peak_time": peak_record["timestamp"],
                "temperature": daily_weather[0]["temperature"],
                "humidity": daily_weather[0]["humidity"],
                "wind_speed": daily_weather[0]["wind_speed"],
                "records": nh_records
            })

        output = {
            "metadata": {
                "city": city_key,
                "state": city_info["state"],
                "station_id": city_info["station_id"],
                "station_name": city_info["station_name"],
                "center": city_info["center"],
                "festival": FESTIVAL_NAME,
                "festival_name": FESTIVAL_NAME,
                "festival_year": FESTIVAL_YEAR,
                "festival_date": FESTIVAL_DATE_STR,
                "diwali_date": FESTIVAL_DATE_STR,
                "start_date": START_DATE_STR,
                "end_date": END_DATE_STR,
                "total_days": TOTAL_TIMELINE_DAYS,
                "timezone": TIMEZONE,
                "timeline_range": {
                    "start": START_DATE_STR,
                    "end": END_DATE_STR,
                    "days_span": TOTAL_TIMELINE_DAYS
                },
                "source_type": "SIMULATED",
                "engine_version": "AetherQI_HeuristicSimulator_v4.0",
                "dispersion_rate": self.dispersion_rate,
                "background_baseline": self.background_baseline,
                "description": (
                    "AetherQI demonstration dataset generated via heuristic formulas. "
                    "Not official government measurements. "
                    "Clearly designated as Simulated Prediction."
                )
            },
            "neighbourhoods": neighbourhood_data
        }

        # Generate city-specific actionable alerts across the 21 days
        output["alerts"] = self.generate_alerts(output)
        return output

    def generate_11_day_dataset(self, city: str = "Delhi") -> Dict[str, Any]:
        """
        Backwards compatibility alias for existing tests and endpoints.
        Delegates to the complete 21-day dataset generation.
        """
        return self.generate_21_day_dataset(city=city)

    def generate_alerts(self, simulated_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates actionable health and dispersion alerts across the full 21-day timeline (T-10 to T+10).
        Calculated dynamically from the central festival configuration date (8 Nov 2026).
        """
        alerts = []
        alert_id = 1
        city_name = simulated_data.get("metadata", {}).get("city", "Selected Location")

        for nh in simulated_data.get("neighbourhoods", []):
            peak_aqi = nh["predicted_peak_aqi"]
            modifier = nh["modifier"]

            # Alert 1: T-7 (1 Nov 2026) – Early Festival Inversion Advisory
            t7_date = (self.diwali_date - timedelta(days=7)).strftime("%Y-%m-%d")
            t7_title = f"Pre-Festival Inversion Advisory: {nh['name']}"
            t7_msg = (
                f"Particulate levels in {nh['name']} are showing early seasonal increase due to autumn "
                f"temperature cooling. Background AQI rising towards moderate/poor thresholds."
            )
            t7_act = "Vulnerable individuals with respiratory sensitivity should schedule outdoor exercise during daytime."
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "ADVISORY",
                "badge_color": "#3B82F6",
                "neighbourhood": nh["name"],
                "city": nh["city"],
                "day_offset": -7,
                "predicted_time": f"{t7_date} (T-7 Days Pre-Diwali)",
                "predicted_aqi": round(175.0 * modifier, 1),
                "title": t7_title,
                "headline": t7_title,
                "message": t7_msg,
                "explanation": t7_msg,
                "action_advised": t7_act,
                "precaution": t7_act,
                "trigger": "Early Festival Seasonal Accumulation (T-7 Days)"
            })
            alert_id += 1

            # Alert 2: T-3 (5 Nov 2026) – Dhanteras & Festive Market Traffic Surge Warning
            t3_date = (self.diwali_date - timedelta(days=3)).strftime("%Y-%m-%d")
            t3_title = f"Dhanteras Market Traffic Warning: {nh['name']}"
            t3_msg = (
                f"Surge in pre-festival retail shopping and delivery transit in {nh['name']} ({nh['type']}) "
                f"is elevating localized NOx and PM2.5 levels. Heavy vehicular idle times expected."
            )
            t3_act = "Utilize non-motorized transport for local shopping; avoid idling engines in market corridors."
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "WARNING",
                "badge_color": "#F97316",
                "neighbourhood": nh["name"],
                "city": nh["city"],
                "day_offset": -3,
                "predicted_time": f"{t3_date} (T-3 Days - Dhanteras)",
                "predicted_aqi": round(220.0 * modifier, 1),
                "title": t3_title,
                "headline": t3_title,
                "message": t3_msg,
                "explanation": t3_msg,
                "action_advised": t3_act,
                "precaution": t3_act,
                "trigger": "Festive Market Vehicular Surge > 85% Density"
            })
            alert_id += 1

            # Alert 3: T0 (8 Nov 2026) – Diwali Night Peak Pollution Spike Warning
            t0_date = self.diwali_date.strftime("%Y-%m-%d")
            t0_title = f"Critical Diwali Night Pollution Alert: {nh['name']}"
            t0_msg = (
                f"Projected peak AQI will surge to {peak_aqi} (Severe category) on Diwali night (8 Nov). "
                f"Calm nocturnal surface winds and shallow thermal boundary layer trap high-density fireworks emissions."
            )
            t0_act = "Avoid all outdoor exertion between 8:00 PM and 2:00 AM; use HEPA air filtration indoors."
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "CRITICAL",
                "badge_color": "#EF4444",
                "neighbourhood": nh["name"],
                "city": nh["city"],
                "day_offset": 0,
                "predicted_time": f"{t0_date}T22:00:00 (Diwali Night 8 PM - 2 AM)",
                "predicted_aqi": peak_aqi,
                "title": t0_title,
                "headline": t0_title,
                "message": t0_msg,
                "explanation": t0_msg,
                "action_advised": t0_act,
                "precaution": t0_act,
                "trigger": f"AQI > 400 Severe Peak Projection ({peak_aqi})"
            })
            alert_id += 1

            # Alert 4: T+2 (10 Nov 2026) – Elevated Smog Persistence Advisory
            t2_date = (self.diwali_date + timedelta(days=2)).strftime("%Y-%m-%d")
            t2_title = f"Post-Festival Smog Stagnation: {nh['name']}"
            t2_msg = (
                f"Residual festival particulates linger over {nh['name']} under light wind conditions. "
                f"Elevated PM2.5 levels continue into early morning hours."
            )
            t2_act = "Wear N95/N99 protective masks if commuting during morning hours; limit children's outdoor playtime."
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "WARNING",
                "badge_color": "#F97316",
                "neighbourhood": nh["name"],
                "city": nh["city"],
                "day_offset": 2,
                "predicted_time": f"{t2_date} (T+2 Days Post-Diwali)",
                "predicted_aqi": round(peak_aqi * 0.72, 1),
                "title": t2_title,
                "headline": t2_title,
                "message": t2_msg,
                "explanation": t2_msg,
                "action_advised": t2_act,
                "precaution": t2_act,
                "trigger": "Residual Festival Smog Inversion (T+2 Days)"
            })
            alert_id += 1

            # Alert 5: T+7 (15 Nov 2026) – Active Atmospheric Dispersion Recovery
            t7p_date = (self.diwali_date + timedelta(days=7)).strftime("%Y-%m-%d")
            t7p_title = f"Atmospheric Clearance Trend: {nh['name']}"
            t7p_msg = (
                f"Strengthening north-westerly wind flows are driving steady atmospheric clearance across {nh['name']}. "
                f"Particulate concentrations demonstrating continuous decline towards pre-festival baseline."
            )
            t7p_act = "Outdoor air quality significantly improving; natural daytime room ventilation recommended."
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "ADVISORY",
                "badge_color": "#10B981",
                "neighbourhood": nh["name"],
                "city": nh["city"],
                "day_offset": 7,
                "predicted_time": f"{t7p_date} (T+7 Days Post-Diwali)",
                "predicted_aqi": round(180.0 * modifier, 1),
                "title": t7p_title,
                "headline": t7p_title,
                "message": t7p_msg,
                "explanation": t7p_msg,
                "action_advised": t7p_act,
                "precaution": t7p_act,
                "trigger": "Active Wind Dispersion & Clearance (T+7 Days)"
            })
            alert_id += 1

            # Alert 6: T+10 (18 Nov 2026) – Baseline Restabilization & Comparison
            t10_date = (self.diwali_date + timedelta(days=10)).strftime("%Y-%m-%d")
            t10_title = f"Baseline Restabilization: {nh['name']}"
            t10_msg = (
                f"Ambient air quality in {nh['name']} has successfully restabilized to pre-festival baseline levels. "
                f"The 21-day Diwali festival dispersion cycle is complete."
            )
            t10_act = "Standard seasonal ambient precautions apply as winter conditions set in."
            alerts.append({
                "id": f"ALT-{alert_id:03d}",
                "severity": "ADVISORY",
                "badge_color": "#10B981",
                "neighbourhood": nh["name"],
                "city": nh["city"],
                "day_offset": 10,
                "predicted_time": f"{t10_date} (T+10 Days Post-Diwali)",
                "predicted_aqi": round(155.0 * modifier, 1),
                "title": t10_title,
                "headline": t10_title,
                "message": t10_msg,
                "explanation": t10_msg,
                "action_advised": t10_act,
                "precaution": t10_act,
                "trigger": "Post-Festival Normalization (T+10 Days)"
            })
            alert_id += 1

        return alerts

def generate_and_save_mock_dataset(output_path: Optional[str] = None):
    if output_path is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
        output_path = str(base_dir / "data" / "mock_data.json")

    simulator = HeuristicPollutionSimulator()
    
    # Generate datasets for all supported cities
    all_city_data = {}
    for city_name in SUPPORTED_CITIES:
        data = simulator.generate_21_day_dataset(city=city_name)
        all_city_data[city_name] = data

    # For default backwards compatibility, top-level reflects Delhi, and has 'cities' map
    default_data = all_city_data["Delhi"]
    combined = dict(default_data)
    combined["cities"] = all_city_data

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    print(f"Generated 21-day multi-city mock dataset for {list(SUPPORTED_CITIES.keys())} at {output_path}")
    return combined

if __name__ == "__main__":
    generate_and_save_mock_dataset()
