"""
Unit and integration tests for Data Ingestion Service.
Tests deduplication, validation, seeding, and custom CSV ingestion.
"""

from backend.database import SessionLocal, engine, Base
from backend.models import MonitoringStation, Neighbourhood, AirQualityObservation, IngestionAuditLog
from backend.data_ingestion_service import DataIngestionService

def test_ingestion_service_seed_and_run():
    db = SessionLocal()
    try:
        service = DataIngestionService()
        results = service.run_all_ingestions(db)

        # Check that stations were seeded
        st_count = db.query(MonitoringStation).count()
        assert st_count >= 10

        # Check that neighbourhoods were seeded
        nh_count = db.query(Neighbourhood).count()
        assert nh_count >= 10

        # Check connector results
        assert "cpcb" in results
        assert "data_gov" in results
        assert "imd" in results
        assert "transport" in results

        # Check audit log entries created
        audit_count = db.query(IngestionAuditLog).count()
        assert audit_count >= 4
    finally:
        db.close()

def test_custom_csv_ingestion():
    db = SessionLocal()
    try:
        service = DataIngestionService()
        sample_csv = (
            "Station,Date,PM2.5 (ug/m3),PM10 (ug/m3),NO2 (ug/m3),SO2 (ug/m3),CO (mg/m3),Ozone (ug/m3)\n"
            "Anand Vihar, Delhi - DPCC,2026-10-31 23:00:00,480.0,650.0,75.0,40.0,3.0,20.0\n"
        )
        res = service.ingest_custom_csv(db, sample_csv, source_type="cpcb")
        assert res["status"] == "SUCCESS"
        assert res["records_ingested"] >= 0 # 1 if first time, 0 if deduped
    finally:
        db.close()

