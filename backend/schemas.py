"""
Pydantic Schemas for Request/Response Validation and Data Transparency.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class MonitoringStationSchema(BaseModel):
    station_id: str
    station_code: Optional[str] = None
    name: str
    city: str
    state: str
    latitude: float
    longitude: float
    agency: str
    station_type: str
    source_url: str
    is_active: bool

    class Config:
        from_attributes = True

class NeighbourhoodSchema(BaseModel):
    id: int
    name: str
    city: str
    state: str
    latitude: float
    longitude: float
    description: Optional[str] = None
    nearest_station_id: Optional[str] = None
    nearest_station_name: Optional[str] = None
    distance_to_nearest_km: Optional[float] = None
    coverage_reliability: str
    type: Optional[str] = None
    modifier: Optional[float] = None

    class Config:
        from_attributes = True

class AirQualityObservationSchema(BaseModel):
    id: Optional[int] = None
    station_id: str
    station_name: Optional[str] = None
    city: Optional[str] = None
    observation_time: datetime
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    co: Optional[float] = None
    o3: Optional[float] = None
    nh3: Optional[float] = None
    cpcb_aqi: Optional[int] = None
    prominent_pollutant: Optional[str] = None
    aqi_category: Optional[str] = None
    source_name: str
    source_url: str
    retrieval_time: datetime
    provenance: str
    freshness_status: Optional[str] = None # LIVE, DELAYED, HISTORICAL, DEMO

    class Config:
        from_attributes = True

class WeatherObservationSchema(BaseModel):
    station_id: str
    city: str
    observation_time: datetime
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    rainfall_mm: Optional[float] = 0.0
    source_name: str
    source_url: str
    provenance: str

    class Config:
        from_attributes = True

class PredictionRequestSchema(BaseModel):
    neighbourhood_or_station: str
    target_date: Optional[str] = None
    scenario: str = Field(default="moderate_ban", description="unrestricted, green_crackers, strict_ban, severe_stagnation")
    hours_ahead: int = Field(default=24, ge=1, le=72)

class PredictionResponseItem(BaseModel):
    timestamp: datetime
    predicted_pm25: float
    predicted_pm10: float
    predicted_cpcb_aqi: int
    prominent_pollutant: str
    aqi_category: str
    scenario: str
    confidence_interval_low: float
    confidence_interval_high: float
    provenance: str = "MODEL_PREDICTED"

class PredictionResponseSchema(BaseModel):
    target_location: str
    location_type: str
    nearest_station_id: Optional[str] = None
    distance_km: Optional[float] = None
    coverage_reliability: str
    scenario_applied: str
    model_name: str
    model_mae: float
    model_rmse: float
    predictions: List[PredictionResponseItem]

class DataSourceAuditItem(BaseModel):
    department: str
    source_name: str
    official_website: str
    dataset_name: str
    integration_type: str # API, Downloaded Archive, Documented Reference
    status: str           # CONNECTED, CONFIGURED_NEEDS_KEY, LOCAL_OFFICIAL_ARCHIVE, UNAVAILABLE
    last_ingestion_time: Optional[datetime] = None
    records_count: int = 0
    legal_terms_url: Optional[str] = None

class DataSourcesSummaryResponse(BaseModel):
    strict_policy_notice: str
    data_sources: List[DataSourceAuditItem]
    audit_logs_recent: List[dict]

