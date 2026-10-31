"""
Automated Data Collection and Ingestion Service.
Orchestrates official Indian Government connectors (CPCB, data.gov.in, IMD, MoRTH).
Validates, standardizes, deduplicates, and commits observations to SQLite.
Maintains comprehensive audit logs for all ingestion runs.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.config import DATA_DIR, REFRESH_INTERVAL_MINUTES
from backend.database import SessionLocal, engine, Base
from backend.models import (
    MonitoringStation,
    Neighbourhood,
    AirQualityObservation,
    WeatherObservation,
    TransportIndicator,
    IngestionAuditLog
)
from backend.connectors.cpcb_connector import CPCBConnector
from backend.connectors.data_gov_connector import DataGovConnector
from backend.connectors.imd_connector import IMDConnector
from backend.connectors.government_transport_connector import GovernmentTransportConnector
from backend.location_mapper import (
    DEFAULT_NEIGHBOURHOODS,
    haversine_distance_km,
    evaluate_coverage_reliability
)

logger = logging.getLogger("diwali_airwatch.ingestion_service")

class DataIngestionService:
    def __init__(self):
        # Create all database tables
        Base.metadata.create_all(bind=engine)
        
        # Instantiate connectors
        self.cpcb_connector = CPCBConnector()
        self.data_gov_connector = DataGovConnector()
        self.imd_connector = IMDConnector()
        self.transport_connector = GovernmentTransportConnector()

    def seed_initial_metadata(self, db: Session):
        """
        Seeds official monitoring stations and standard neighbourhoods into database if empty.
        """
        # 1. Seed Stations
        station_count = db.query(MonitoringStation).count()
        if station_count == 0:
            stations_file = DATA_DIR / "official_cpcb_stations.json"
            if stations_file.exists():
                with open(stations_file, "r", encoding="utf-8") as f:
                    stations_data = json.load(f)
                for st in stations_data:
                    station_obj = MonitoringStation(
                        station_id=st["station_id"],
                        station_code=st.get("station_code"),
                        name=st["name"],
                        city=st["city"],
                        state=st["state"],
                        latitude=st["latitude"],
                        longitude=st["longitude"],
                        agency=st.get("agency", "CPCB"),
                        station_type=st.get("station_type", "CAAQMS"),
                        source_url=st.get("source_url", "https://cpcb.nic.in/"),
                        is_active=True
                    )
                    db.add(station_obj)
                db.commit()
                logger.info(f"Seeded {len(stations_data)} official CPCB stations.")

        # 2. Seed Neighbourhoods
        neighbourhood_count = db.query(Neighbourhood).count()
        if neighbourhood_count == 0:
            all_stations = db.query(MonitoringStation).all()
            for nh in DEFAULT_NEIGHBOURHOODS:
                # Find nearest station
                nearest_st = None
                min_dist = float("inf")
                for st in all_stations:
                    dist = haversine_distance_km(nh["latitude"], nh["longitude"], st.latitude, st.longitude)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_st = st

                reliability = evaluate_coverage_reliability(min_dist)
                nh_obj = Neighbourhood(
                    name=nh["name"],
                    city=nh["city"],
                    state=nh["state"],
                    latitude=nh["latitude"],
                    longitude=nh["longitude"],
                    description=nh.get("description"),
                    nearest_station_id=nearest_st.station_id if nearest_st else None,
                    distance_to_nearest_km=min_dist if nearest_st else None,
                    coverage_reliability=reliability
                )
                db.add(nh_obj)
            db.commit()
            logger.info(f"Seeded {len(DEFAULT_NEIGHBOURHOODS)} urban neighbourhoods with spatial mappings.")

    def run_all_ingestions(self, db: Session) -> Dict[str, Any]:
        """
        Executes ingestion sequence across all 4 connectors and records audit logs.
        """
        results = {}
        self.seed_initial_metadata(db)

        # 1. CPCB CAAQMS Ingestion
        results["cpcb"] = self._ingest_cpcb(db)

        # 2. Government Open Data Platform (data.gov.in) Ingestion
        results["data_gov"] = self._ingest_data_gov(db)

        # 3. IMD Weather Ingestion
        results["imd"] = self._ingest_imd(db)

        # 4. MoRTH Transport Indicators Ingestion
        results["transport"] = self._ingest_transport(db)

        return results

    def _ingest_cpcb(self, db: Session) -> Dict[str, Any]:
        start_time = time.time()
        try:
            res = self.cpcb_connector.fetch_live_data()
            records = res.get("records", [])
            inserted = 0

            for r in records:
                if self._validate_air_quality_record(r):
                    if not self._observation_exists(db, r["dedup_hash"]):
                        # Ensure station exists in DB
                        self._ensure_station_exists(db, r)
                        obs = AirQualityObservation(
                            station_id=r["station_id"],
                            observation_time=r["observation_time"],
                            pm25=r.get("pm25"),
                            pm10=r.get("pm10"),
                            no2=r.get("no2"),
                            so2=r.get("so2"),
                            co=r.get("co"),
                            o3=r.get("o3"),
                            nh3=r.get("nh3"),
                            cpcb_aqi=r.get("cpcb_aqi"),
                            prominent_pollutant=r.get("prominent_pollutant"),
                            aqi_category=r.get("aqi_category"),
                            source_name=r["source_name"],
                            source_url=r["source_url"],
                            retrieval_time=r.get("retrieval_time", datetime.utcnow()),
                            provenance=r["provenance"],
                            is_valid=True,
                            dedup_hash=r["dedup_hash"]
                        )
                        db.add(obs)
                        inserted += 1

            db.commit()
            elapsed = round(time.time() - start_time, 2)
            status = "SUCCESS" if inserted > 0 else res.get("status", "SUCCESS")
            
            self._log_audit(
                db,
                connector_name="CPCB_CAAQMS_Connector",
                status=status,
                records_ingested=inserted,
                source_url=res.get("source_url"),
                execution_time=elapsed,
                error_msg=None if status == "SUCCESS" else res.get("message")
            )

            return {
                "status": status,
                "records_ingested": inserted,
                "provenance": res.get("provenance"),
                "source_url": res.get("source_url"),
                "message": res.get("message")
            }
        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            logger.error(f"Error in CPCB ingestion: {e}")
            self._log_audit(db, "CPCB_CAAQMS_Connector", "FAILED", 0, self.cpcb_connector.source_url, elapsed, str(e))
            return {"status": "FAILED", "records_ingested": 0, "error": str(e)}

    def _ingest_data_gov(self, db: Session) -> Dict[str, Any]:
        start_time = time.time()
        try:
            res = self.data_gov_connector.fetch_live_data()
            records = res.get("records", [])
            inserted = 0

            for r in records:
                if self._validate_air_quality_record(r):
                    if not self._observation_exists(db, r["dedup_hash"]):
                        self._ensure_station_exists(db, r)
                        obs = AirQualityObservation(
                            station_id=r["station_id"],
                            observation_time=r["observation_time"],
                            pm25=r.get("pm25"),
                            pm10=r.get("pm10"),
                            no2=r.get("no2"),
                            so2=r.get("so2"),
                            co=r.get("co"),
                            o3=r.get("o3"),
                            nh3=r.get("nh3"),
                            cpcb_aqi=r.get("cpcb_aqi"),
                            prominent_pollutant=r.get("prominent_pollutant"),
                            aqi_category=r.get("aqi_category"),
                            source_name=r["source_name"],
                            source_url=r["source_url"],
                            retrieval_time=r.get("retrieval_time", datetime.utcnow()),
                            provenance=r["provenance"],
                            is_valid=True,
                            dedup_hash=r["dedup_hash"]
                        )
                        db.add(obs)
                        inserted += 1

            db.commit()
            elapsed = round(time.time() - start_time, 2)
            status = res.get("status", "SUCCESS")
            
            self._log_audit(
                db,
                connector_name="DataGov_RealTime_AQI_Connector",
                status=status,
                records_ingested=inserted,
                source_url=res.get("source_url"),
                execution_time=elapsed,
                error_msg=None if status == "SUCCESS" else res.get("message")
            )

            return {
                "status": status,
                "records_ingested": inserted,
                "provenance": res.get("provenance"),
                "source_url": res.get("source_url"),
                "message": res.get("message")
            }
        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            logger.error(f"Error in data.gov.in ingestion: {e}")
            self._log_audit(db, "DataGov_RealTime_AQI_Connector", "FAILED", 0, self.data_gov_connector.source_url, elapsed, str(e))
            return {"status": "FAILED", "records_ingested": 0, "error": str(e)}

    def _ingest_imd(self, db: Session) -> Dict[str, Any]:
        start_time = time.time()
        try:
            res = self.imd_connector.fetch_live_data()
            records = res.get("records", [])
            inserted = 0

            for r in records:
                if not db.query(WeatherObservation).filter_by(dedup_hash=r["dedup_hash"]).first():
                    w_obs = WeatherObservation(
                        station_id=r["station_id"],
                        city=r["city"],
                        observation_time=r["observation_time"],
                        temperature_c=r.get("temperature_c"),
                        humidity_pct=r.get("humidity_pct"),
                        wind_speed_kmh=r.get("wind_speed_kmh"),
                        wind_direction_deg=r.get("wind_direction_deg"),
                        rainfall_mm=r.get("rainfall_mm", 0.0),
                        source_name=r["source_name"],
                        source_url=r["source_url"],
                        retrieval_time=r.get("retrieval_time", datetime.utcnow()),
                        provenance=r["provenance"],
                        dedup_hash=r["dedup_hash"]
                    )
                    db.add(w_obs)
                    inserted += 1

            db.commit()
            elapsed = round(time.time() - start_time, 2)
            status = res.get("status", "SUCCESS")

            self._log_audit(
                db,
                connector_name="IMD_Weather_Connector",
                status=status,
                records_ingested=inserted,
                source_url=res.get("source_url"),
                execution_time=elapsed,
                error_msg=None if status == "SUCCESS" else res.get("message")
            )

            return {
                "status": status,
                "records_ingested": inserted,
                "provenance": res.get("provenance"),
                "source_url": res.get("source_url"),
                "message": res.get("message")
            }
        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            logger.error(f"Error in IMD ingestion: {e}")
            self._log_audit(db, "IMD_Weather_Connector", "FAILED", 0, self.imd_connector.source_url, elapsed, str(e))
            return {"status": "FAILED", "records_ingested": 0, "error": str(e)}

    def _ingest_transport(self, db: Session) -> Dict[str, Any]:
        start_time = time.time()
        try:
            res = self.transport_connector.fetch_live_data()
            records = res.get("records", [])
            inserted = 0

            for r in records:
                t_obj = TransportIndicator(
                    city=r["city"],
                    area_name=r["area_name"],
                    timestamp=r["timestamp"],
                    congestion_level=r["congestion_level"],
                    relative_density_score=r["relative_density_score"],
                    source_name=r["source_name"],
                    source_url=r["source_url"],
                    provenance=r["provenance"],
                    notes=r.get("notes")
                )
                db.add(t_obj)
                inserted += 1

            db.commit()
            elapsed = round(time.time() - start_time, 2)

            self._log_audit(
                db,
                connector_name="Government_Transport_Connector",
                status="SUCCESS",
                records_ingested=inserted,
                source_url=res.get("source_url"),
                execution_time=elapsed,
                error_msg=None
            )

            return {
                "status": "SUCCESS",
                "records_ingested": inserted,
                "provenance": res.get("provenance"),
                "source_url": res.get("source_url"),
                "message": res.get("message")
            }
        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            logger.error(f"Error in Transport ingestion: {e}")
            self._log_audit(db, "Government_Transport_Connector", "FAILED", 0, self.transport_connector.source_url, elapsed, str(e))
            return {"status": "FAILED", "records_ingested": 0, "error": str(e)}

    def ingest_custom_csv(self, db: Session, file_content: str, source_type: str = "cpcb") -> Dict[str, Any]:
        """
        Allows importing officially downloaded CSV files from CPCB or data.gov.in.
        """
        start_time = time.time()
        try:
            if source_type.lower() == "data_gov":
                records = self.data_gov_connector.parse_csv_file(file_content)
                connector_name = "DataGov_CSV_Import"
            else:
                records = self.cpcb_connector.parse_csv_file(file_content)
                connector_name = "CPCB_CSV_Import"

            inserted = 0
            for r in records:
                if self._validate_air_quality_record(r):
                    if not self._observation_exists(db, r["dedup_hash"]):
                        self._ensure_station_exists(db, r)
                        obs = AirQualityObservation(
                            station_id=r["station_id"],
                            observation_time=r["observation_time"],
                            pm25=r.get("pm25"),
                            pm10=r.get("pm10"),
                            no2=r.get("no2"),
                            so2=r.get("so2"),
                            co=r.get("co"),
                            o3=r.get("o3"),
                            nh3=r.get("nh3"),
                            cpcb_aqi=r.get("cpcb_aqi"),
                            prominent_pollutant=r.get("prominent_pollutant"),
                            aqi_category=r.get("aqi_category"),
                            source_name=r["source_name"],
                            source_url=r["source_url"],
                            retrieval_time=r.get("retrieval_time", datetime.utcnow()),
                            provenance="OFFICIAL_CSV_IMPORT",
                            is_valid=True,
                            dedup_hash=r["dedup_hash"]
                        )
                        db.add(obs)
                        inserted += 1

            db.commit()
            elapsed = round(time.time() - start_time, 2)
            self._log_audit(db, connector_name, "SUCCESS", inserted, "User Uploaded Official CSV", elapsed, None)

            return {
                "status": "SUCCESS",
                "records_parsed": len(records),
                "records_ingested": inserted,
                "message": f"Successfully imported {inserted} new valid records from official government CSV."
            }
        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            logger.error(f"Error importing custom CSV: {e}")
            self._log_audit(db, "Custom_CSV_Import", "FAILED", 0, "Uploaded CSV", elapsed, str(e))
            return {"status": "FAILED", "records_ingested": 0, "error": str(e)}

    def _validate_air_quality_record(self, r: Dict[str, Any]) -> bool:
        """
        Validates values against physical bounds for atmospheric pollutants.
        """
        # PM2.5: reasonable range 0 to 1500 µg/m³
        if r.get("pm25") is not None and not (0 <= r["pm25"] <= 1500):
            return False
        # PM10: reasonable range 0 to 2500 µg/m³
        if r.get("pm10") is not None and not (0 <= r["pm10"] <= 2500):
            return False
        return True

    def _observation_exists(self, db: Session, dedup_hash: str) -> bool:
        return db.query(AirQualityObservation).filter_by(dedup_hash=dedup_hash).first() is not None

    def _ensure_station_exists(self, db: Session, r: Dict[str, Any]):
        st_id = r["station_id"]
        existing = db.query(MonitoringStation).filter_by(station_id=st_id).first()
        if not existing:
            new_st = MonitoringStation(
                station_id=st_id,
                name=r.get("station_name", "CPCB Monitoring Station"),
                city=r.get("city", "Delhi"),
                state=r.get("state", "Delhi"),
                latitude=28.6139,
                longitude=77.2090,
                agency="CPCB / State Pollution Control Board",
                station_type="CAAQMS",
                source_url=r.get("source_url", "https://cpcb.nic.in/"),
                is_active=True
            )
            db.add(new_st)
            db.commit()

    def _log_audit(
        self,
        db: Session,
        connector_name: str,
        status: str,
        records_ingested: int,
        source_url: Optional[str],
        execution_time: float,
        error_msg: Optional[str]
    ):
        audit = IngestionAuditLog(
            connector_name=connector_name,
            status=status,
            records_ingested=records_ingested,
            error_message=error_msg,
            source_url=source_url,
            execution_time_seconds=execution_time,
            timestamp=datetime.utcnow()
        )
        db.add(audit)
        db.commit()

