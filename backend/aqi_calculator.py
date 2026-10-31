"""
Official Central Pollution Control Board (CPCB) National Air Quality Index (IND-AQI) Calculator.
Adheres strictly to MoEFCC / CPCB 2014-2015 published methodology.

Mandate:
- Sub-indices are calculated for PM2.5, PM10, NO2, SO2, CO, O3, and NH3.
- Official overall AQI REQUIRES at least 3 pollutants to be monitored,
  one of which MUST be either PM2.5 or PM10.
- NEVER calculate official overall AQI from PM2.5 alone.
"""

from typing import Dict, Optional, Tuple, Any

# Breakpoint table: (C_low, C_high, I_low, I_high)
CPCB_BREAKPOINTS = {
    "PM2.5": [
        (0.0, 30.0, 0, 50),
        (30.1, 60.0, 51, 100),
        (60.1, 90.0, 101, 200),
        (90.1, 120.0, 201, 300),
        (120.1, 250.0, 301, 400),
        (250.1, 500.0, 401, 500),
    ],
    "PM10": [
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (100.1, 250.0, 101, 200),
        (250.1, 350.0, 201, 300),
        (350.1, 430.0, 301, 400),
        (430.1, 600.0, 401, 500),
    ],
    "NO2": [
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 180.0, 101, 200),
        (180.1, 280.0, 201, 300),
        (280.1, 400.0, 301, 400),
        (400.1, 600.0, 401, 500),
    ],
    "SO2": [
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 380.0, 101, 200),
        (380.1, 800.0, 201, 300),
        (800.1, 1600.0, 301, 400),
        (1600.1, 2500.0, 401, 500),
    ],
    "CO": [
        (0.0, 1.0, 0, 50),
        (1.01, 2.0, 51, 100),
        (2.01, 10.0, 101, 200),
        (10.01, 17.0, 201, 300),
        (17.01, 34.0, 301, 400),
        (34.01, 50.0, 401, 500),
    ],
    "O3": [
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (100.1, 168.0, 101, 200),
        (168.1, 208.0, 201, 300),
        (208.1, 748.0, 301, 400),
        (748.1, 1000.0, 401, 500),
    ],
    "NH3": [
        (0.0, 200.0, 0, 50),
        (200.1, 400.0, 51, 100),
        (400.1, 800.0, 101, 200),
        (800.1, 1200.0, 201, 300),
        (1200.1, 1800.0, 301, 400),
        (1800.1, 2500.0, 401, 500),
    ]
}

def calculate_sub_index(pollutant: str, concentration: Optional[float]) -> Optional[int]:
    """
    Calculate sub-index for a single pollutant using CPCB piecewise linear formula:
    I = I_low + ((I_high - I_low) / (C_high - C_low)) * (C - C_low)
    """
    if concentration is None or concentration < 0:
        return None

    breakpoints = CPCB_BREAKPOINTS.get(pollutant.upper())
    if not breakpoints:
        return None

    # Handle concentrations below first bracket or above last bracket
    if concentration <= breakpoints[0][0]:
        return breakpoints[0][2]
    
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= concentration <= c_high:
            sub_index = i_low + ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low)
            return round(sub_index)

    # If concentration exceeds highest threshold, cap at 500
    return 500

def get_aqi_category(aqi_value: Optional[int]) -> Tuple[str, str]:
    """
    Returns (Category Name, Hex Color) as defined by CPCB.
    """
    if aqi_value is None:
        return ("Unknown", "#808080")
    if 0 <= aqi_value <= 50:
        return ("Good", "#00B050")
    elif 51 <= aqi_value <= 100:
        return ("Satisfactory", "#92D050")
    elif 101 <= aqi_value <= 200:
        return ("Moderate", "#FFFF00")
    elif 201 <= aqi_value <= 300:
        return ("Poor", "#FF9900")
    elif 301 <= aqi_value <= 400:
        return ("Very Poor", "#FF0000")
    else:
        return ("Severe", "#C00000")

def calculate_cpcb_aqi(pollutants: Dict[str, Optional[float]]) -> Dict[str, Any]:
    """
    Compute official CPCB IND-AQI according to regulatory requirements:
    1. Calculate sub-index for every available pollutant.
    2. Check minimum pollutant criteria:
       - Total pollutants >= 3
       - At least one must be PM2.5 or PM10
    3. If valid, AQI = max(sub-indices), prominent = argmax(sub-indices)
    4. If invalid, return provisional sub-indices and explain the missing parameters.
    """
    sub_indices: Dict[str, int] = {}
    
    # Standardize keys
    key_mapping = {
        "pm25": "PM2.5",
        "pm2.5": "PM2.5",
        "pm10": "PM10",
        "no2": "NO2",
        "so2": "SO2",
        "co": "CO",
        "o3": "O3",
        "ozone": "O3",
        "nh3": "NH3"
    }

    cleaned_pollutants: Dict[str, float] = {}
    for k, v in pollutants.items():
        standard_k = key_mapping.get(k.lower(), k.upper())
        if v is not None and v >= 0:
            cleaned_pollutants[standard_k] = float(v)

    for p_name, val in cleaned_pollutants.items():
        s_idx = calculate_sub_index(p_name, val)
        if s_idx is not None:
            sub_indices[p_name] = s_idx

    has_pm = ("PM2.5" in sub_indices) or ("PM10" in sub_indices)
    pollutant_count = len(sub_indices)

    if pollutant_count >= 3 and has_pm:
        # Fully compliant official CPCB calculation
        prominent = max(sub_indices, key=sub_indices.get)
        official_aqi = min(500, sub_indices[prominent])
        category, color = get_aqi_category(official_aqi)
        return {
            "aqi": official_aqi,
            "category": category,
            "color": color,
            "prominent_pollutant": prominent,
            "sub_indices": sub_indices,
            "is_official_compliant": True,
            "compliance_note": "Meets CPCB criteria (>=3 parameters including PM2.5/PM10)"
        }
    elif has_pm:
        # Partial parameters: PM available, but total < 3
        prominent = max(sub_indices, key=sub_indices.get)
        provisional_val = min(500, sub_indices[prominent])
        category, color = get_aqi_category(provisional_val)
        return {
            "aqi": provisional_val,
            "category": f"{category} (Provisional)",
            "color": color,
            "prominent_pollutant": f"{prominent} (Sub-Index Only)",
            "sub_indices": sub_indices,
            "is_official_compliant": False,
            "compliance_note": f"Incomplete for Official CPCB AQI: Only {pollutant_count} pollutant(s) available. CPCB mandates at least 3 pollutants."
        }
    else:
        # Ineligible
        return {
            "aqi": None,
            "category": "Insufficient Data",
            "color": "#808080",
            "prominent_pollutant": "None",
            "sub_indices": sub_indices,
            "is_official_compliant": False,
            "compliance_note": "Neither PM2.5 nor PM10 available. Cannot compute air quality index."
        }

