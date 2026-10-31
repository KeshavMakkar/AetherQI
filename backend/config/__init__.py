"""
Configuration and Environment Settings for AetherQI.
Strict Government Data Integration and Provenance Tracking.
Includes central festival configuration and timeline settings.
"""

import os
from pathlib import Path

# Note: Since this is now backend/config/__init__.py:
# parent is backend/config
# parent.parent is backend
# parent.parent.parent is root workspace directory D:\Rootaccess'26
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Government API Configuration
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "")
DATA_GOV_RESOURCE_ID = os.getenv("DATA_GOV_RESOURCE_ID", "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69")
DATA_GOV_BASE_URL = "https://api.data.gov.in/resource"

IMD_API_KEY = os.getenv("IMD_API_KEY", "")
IMD_API_BASE_URL = "https://api.imd.gov.in/public/index.php"

CPCB_CCR_URL = "https://app.cpcbccr.com/caaqms"
CPCB_MAIN_URL = "https://cpcb.nic.in"
MOEFCC_URL = "https://moef.gov.in"
MORTH_URL = "https://morth.nic.in"

# Database Configuration
DATABASE_PATH = BASE_DIR / "diwali_airwatch.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

# Ingestion & Refresh Schedules
REFRESH_INTERVAL_MINUTES = int(os.getenv("REFRESH_INTERVAL_MINUTES", "30"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "3"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "1"))

# Spatial and Quality Parameters
MAX_STATION_RADIUS_KM = float(os.getenv("MAX_STATION_RADIUS_KM", "25.0"))
ALLOW_DEMO_DATA = os.getenv("ALLOW_DEMO_DATA", "True").lower() in ("true", "1", "yes")

# Data Provenance Classification Constants
PROVENANCE_DIRECT = "DIRECTLY_MEASURED"
PROVENANCE_PREDICTED = "MODEL_PREDICTED"
PROVENANCE_ESTIMATED = "SPATIALLY_ESTIMATED"
PROVENANCE_HISTORICAL = "HISTORICAL_GOVERNMENT_RECORD"
PROVENANCE_DEMO = "DEMO_SYNTHETIC"

# Freshness Classification Thresholds (in hours)
FRESHNESS_LIVE_HOURS = 1.0
FRESHNESS_DELAYED_HOURS = 4.0
FRESHNESS_STALE_HOURS = 12.0

# Central Festival Configuration Exports
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
    FESTIVAL_CONFIG,
    get_festival_date,
    get_festival_timezone,
    get_timeline_date_range,
    get_timeline_calendar_days,
    get_festival_config
)

# Central Cities Configuration Exports (All 20 Metropolitan Cities)
from backend.config.cities_config import (
    CITIES_REGISTRY,
    get_all_cities_list,
    get_city_config
)

