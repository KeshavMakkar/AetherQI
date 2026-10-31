"""
SQLAlchemy ORM models for Diwali AirWatch.
Mandatory Provenance, Source URL, and Quality Audit Tracking on all records.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from backend.database import Base

class MonitoringStation(Base):
    __tablename__ = "monitoring_stations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. CPCB_DL_001
    station_code = Column(String(50), index=True)                           # e.g. DL001
    name = Column(String(200), nullable=False)
    city = Column(String(100), index=True, nullable=False)
    state = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    agency = Column(String(150), nullable=False)                            # e.g. DPCC / CPCB
    station_type = Column(String(100), default="CAAQMS")
    source_url = Column(String(300), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    observations = relationship("AirQualityObservation", back_populates="station", cascade="all, delete-orphan")

class Neighbourhood(Base):
    __tablename__ = "neighbourhoods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    city = Column(String(100), index=True, nullable=False)
    state = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(String(250), nullable=True)
    nearest_station_id = Column(String(50), ForeignKey("monitoring_stations.station_id"), nullable=True)
    distance_to_nearest_km = Column(Float, nullable=True)
    coverage_reliability = Column(String(50), default="HIGH") # HIGH (<5km), MEDIUM (5-15km), ESTIMATED (>15km)
    created_at = Column(DateTime, default=datetime.utcnow)

class AirQualityObservation(Base):
    __tablename__ = "air_quality_observations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), ForeignKey("monitoring_stations.station_id"), index=True, nullable=False)
    observation_time = Column(DateTime, index=True, nullable=False)
    
    # Measured Pollutant Concentrations
    pm25 = Column(Float, nullable=True)     # µg/m³
    pm10 = Column(Float, nullable=True)     # µg/m³
    no2 = Column(Float, nullable=True)      # µg/m³
    so2 = Column(Float, nullable=True)      # µg/m³
    co = Column(Float, nullable=True)       # mg/m³
    o3 = Column(Float, nullable=True)       # µg/m³
    nh3 = Column(Float, nullable=True)      # µg/m³

    # CPCB Standard Calculated Indices
    cpcb_aqi = Column(Integer, nullable=True)
    prominent_pollutant = Column(String(50), nullable=True)
    aqi_category = Column(String(50), nullable=True) # Good, Satisfactory, Moderate, Poor, Very Poor, Severe

    # Strict Provenance and Audit Trail
    source_name = Column(String(150), nullable=False) # e.g. "CPCB CCR Portal", "data.gov.in Real-Time AQI"
    source_url = Column(String(300), nullable=False)
    retrieval_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    provenance = Column(String(50), nullable=False)    # DIRECTLY_MEASURED, SPATIALLY_ESTIMATED, HISTORICAL_GOVERNMENT_RECORD, DEMO_SYNTHETIC
    
    # Quality Assurance / Validation
    is_valid = Column(Boolean, default=True)
    validation_notes = Column(Text, nullable=True)
    dedup_hash = Column(String(64), index=True, unique=True, nullable=False) # sha256(station_id + observation_time + source)

    station = relationship("MonitoringStation", back_populates="observations")

    __table_args__ = (
        Index("idx_station_time", "station_id", "observation_time"),
    )

class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), index=True, nullable=False) # e.g. IMD_DL_SAF
    city = Column(String(100), index=True, nullable=False)
    observation_time = Column(DateTime, index=True, nullable=False)
    
    # Meteorological Parameters
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    wind_speed_kmh = Column(Float, nullable=True)
    wind_direction_deg = Column(Float, nullable=True)
    rainfall_mm = Column(Float, default=0.0)

    # Provenance
    source_name = Column(String(150), default="India Meteorological Department (IMD)")
    source_url = Column(String(300), nullable=False)
    retrieval_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    provenance = Column(String(50), default="DIRECTLY_MEASURED")
    dedup_hash = Column(String(64), index=True, unique=True, nullable=False)

class TransportIndicator(Base):
    __tablename__ = "transport_indicators"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), index=True, nullable=False)
    area_name = Column(String(150), nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    
    # Government-published transport metrics
    congestion_level = Column(String(50), default="MODERATE") # LOW, MODERATE, HIGH, SEVERE
    relative_density_score = Column(Float, default=1.0)       # 1.0 = baseline normal
    source_name = Column(String(200), default="MoRTH / Municipal Smart Cities Open Transport Portal")
    source_url = Column(String(300), default="https://morth.nic.in")
    provenance = Column(String(50), default="HISTORICAL_GOVERNMENT_RECORD")
    notes = Column(Text, nullable=True)

class IngestionAuditLog(Base):
    __tablename__ = "ingestion_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    connector_name = Column(String(100), index=True, nullable=False)
    status = Column(String(50), index=True, nullable=False) # SUCCESS, FAILED, SOURCE_UNAVAILABLE, RETRIED
    records_ingested = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    source_url = Column(String(300), nullable=True)
    execution_time_seconds = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(Integer, primary_key=True, index=True)
    target_datetime = Column(DateTime, index=True, nullable=False)
    location_identifier = Column(String(150), index=True, nullable=False) # Station Code or Neighbourhood Name
    location_type = Column(String(50), default="NEIGHBOURHOOD")          # NEIGHBOURHOOD or STATION
    scenario_name = Column(String(50), nullable=False)                    # strict_ban, green_crackers, unrestricted
    
    # Predicted Metrics
    predicted_pm25 = Column(Float, nullable=False)
    predicted_pm10 = Column(Float, nullable=False)
    predicted_cpcb_aqi = Column(Integer, nullable=False)
    prominent_pollutant = Column(String(50), default="PM2.5")
    confidence_interval_low = Column(Float, nullable=True)
    confidence_interval_high = Column(Float, nullable=True)
    
    model_version = Column(String(50), default="RandomForest_v1.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    provenance = Column(String(50), default="MODEL_PREDICTED")

