"""
Government Open Data Platform (data.gov.in) Connector.
Catalog: https://www.data.gov.in/catalog/real-time-air-quality-index
Official Dataset Resource ID: 3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69
Official API: https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69
"""

import csv
import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.config import (
    DATA_GOV_API_KEY, DATA_GOV_RESOURCE_ID, DATA_GOV_BASE_URL,
    DATA_DIR, PROVENANCE_DIRECT, PROVENANCE_HISTORICAL
)
from backend.connectors.base_connector import BaseGovernmentConnector
from backend.aqi_calculator import calculate_cpcb_aqi

logger = logging.getLogger("diwali_airwatch.data_gov_connector")

class DataGovConnector(BaseGovernmentConnector):
    def __init__(self):
        super().__init__(
            name="DataGov_RealTime_AQI_Connector",
            source_url="https://www.data.gov.in/catalog/real-time-air-quality-index",
            department="National Informatics Centre (NIC) / Ministry of Electronics and IT / CPCB"
        )
        self.api_key = DATA_GOV_API_KEY
        self.resource_id = DATA_GOV_RESOURCE_ID
        self.stations_file = DATA_DIR / "official_cpcb_stations.json"
        self._load_stations()

    def _load_stations(self):
        if self.stations_file.exists():
            with open(self.stations_file, "r", encoding="utf-8") as f:
                self.stations_metadata = json.load(f)
        else:
            self.stations_metadata = []

    def fetch_live_data(self) -> Dict[str, Any]:
        """
        Queries official data.gov.in API with authentication key.
        If API key is missing or portal returns auth error, documents the requirement
        and serves verified official data.gov.in catalog records.
        """
        api_url = f"{DATA_GOV_BASE_URL}/{self.resource_id}"

        if not self.api_key:
            logger.info(f"[{self.name}] No DATA_GOV_API_KEY configured in environment.")
            sample_records = self._load_sample_data_gov_records()
            return {
                "status": "CONFIGURED_NEEDS_KEY",
                "api_endpoint": api_url,
                "records": sample_records,
                "source_url": self.source_url,
                "provenance": PROVENANCE_HISTORICAL,
                "retrieval_time": datetime.utcnow().isoformat(),
                "message": (
                    "Official data.gov.in API requires a registered API key. "
                    "Obtain a free key at https://data.gov.in/user/register and set DATA_GOV_API_KEY=<key>. "
                    "Currently displaying verified government sample records from data.gov.in catalog."
                )
            }

        params = {
            "api-key": self.api_key,
            "format": "json",
            "offset": "0",
            "limit": "100"
        }

        response = self.make_http_request(api_url, params=params, max_retries=2)

        if response and response.status_code == 200:
            try:
                data = response.json()
                parsed_records = self._parse_data_gov_json(data)
                return {
                    "status": "SUCCESS",
                    "records": parsed_records,
                    "source_url": self.source_url,
                    "provenance": PROVENANCE_DIRECT,
                    "retrieval_time": datetime.utcnow().isoformat(),
                    "message": f"Successfully retrieved {len(parsed_records)} observations from official data.gov.in API."
                }
            except Exception as e:
                logger.error(f"[{self.name}] Error parsing JSON from data.gov.in: {e}")

        # Fallback if request fails
        sample_records = self._load_sample_data_gov_records()
        return {
            "status": "SOURCE_UNAVAILABLE",
            "api_endpoint": api_url,
            "records": sample_records,
            "source_url": self.source_url,
            "provenance": PROVENANCE_HISTORICAL,
            "retrieval_time": datetime.utcnow().isoformat(),
            "message": "data.gov.in API request unsuccessful. Serving official data.gov.in catalog records."
        }

    def _parse_data_gov_json(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parses data.gov.in Real-Time Air Quality Index schema.
        Rows typically group by station and list multiple pollutants across rows.
        """
        raw_records = data.get("records", [])
        return self._group_and_parse_pollutant_rows(raw_records, source_tag="DATA_GOV_API")

    def parse_csv_file(self, file_path_or_content: Any) -> List[Dict[str, Any]]:
        """
        Parses officially downloaded CSV file from data.gov.in catalog.
        """
        raw_rows = []
        if isinstance(file_path_or_content, (str, Path)) and Path(file_path_or_content).exists():
            with open(file_path_or_content, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                raw_rows = list(reader)
        elif isinstance(file_path_or_content, str):
            reader = csv.DictReader(io.StringIO(file_path_or_content))
            raw_rows = list(reader)

        logger.info(f"[{self.name}] Parsed {len(raw_rows)} raw rows from data.gov.in CSV.")
        return self._group_and_parse_pollutant_rows(raw_rows, source_tag="DATA_GOV_CSV")

    def _group_and_parse_pollutant_rows(self, rows: List[Dict[str, Any]], source_tag: str) -> List[Dict[str, Any]]:
        """
        data.gov.in returns one row per pollutant per station.
        This function groups them by (station, last_update) into unified observation records.
        """
        grouped = {}
        now = datetime.utcnow()

        for r in rows:
            station_name = r.get("station") or r.get("Station") or "Unknown Station"
            city = r.get("city") or r.get("City") or "Delhi"
            state = r.get("state") or r.get("State") or "Delhi"
            last_update = r.get("last_update") or r.get("Date") or now.strftime("%Y-%m-%d %H:%M:%S")

            key = (station_name.strip(), last_update.strip())
            if key not in grouped:
                grouped[key] = {
                    "station_name": station_name.strip(),
                    "city": city.strip(),
                    "state": state.strip(),
                    "last_update": last_update.strip(),
                    "pollutants": {}
                }

            poll_id = (r.get("pollutant_id") or r.get("Pollutant") or "").upper().strip()
            # Try poll_avg, then avg_value, then value
            val = r.get("poll_avg") or r.get("avg_value") or r.get("value") or r.get("poll_min")
            try:
                if val is not None and str(val).strip() != "":
                    grouped[key]["pollutants"][poll_id] = float(val)
            except (ValueError, TypeError):
                pass

        results = []
        for (st_name, update_str), grp in grouped.items():
            try:
                obs_dt = datetime.strptime(update_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                obs_dt = now

            p = grp["pollutants"]
            pm25 = p.get("PM2.5") or p.get("PM25")
            pm10 = p.get("PM10")
            no2 = p.get("NO2")
            so2 = p.get("SO2")
            co = p.get("CO")
            o3 = p.get("OZONE") or p.get("O3")
            nh3 = p.get("NH3")

            # Match station_id from metadata if available
            st_id = f"DATA_GOV_{st_name.replace(' ', '_').upper()[:15]}"
            for meta in self.stations_metadata:
                m_name = meta.get("name", "")
                if m_name and st_name and (m_name.lower() in st_name.lower() or st_name.lower() in m_name.lower()):
                    st_id = meta["station_id"]
                    break

            aqi_res = calculate_cpcb_aqi({"pm25": pm25, "pm10": pm10, "no2": no2, "so2": so2, "co": co, "o3": o3, "nh3": nh3})

            results.append({
                "station_id": st_id,
                "station_name": st_name,
                "city": grp["city"],
                "state": grp["state"],
                "observation_time": obs_dt,
                "pm25": pm25,
                "pm10": pm10,
                "no2": no2,
                "so2": so2,
                "co": co,
                "o3": o3,
                "nh3": nh3,
                "cpcb_aqi": aqi_res["aqi"],
                "prominent_pollutant": aqi_res["prominent_pollutant"],
                "aqi_category": aqi_res["category"],
                "source_name": "Government Open Data Platform (data.gov.in)",
                "source_url": self.source_url,
                "retrieval_time": now,
                "provenance": PROVENANCE_DIRECT if "API" in source_tag else "OFFICIAL_CSV_IMPORT",
                "dedup_hash": self.compute_dedup_hash(st_id, obs_dt, source_tag)
            })

        return results

    def _load_sample_data_gov_records(self) -> List[Dict[str, Any]]:
        sample_path = DATA_DIR / "samples" / "data_gov_aqi_sample.csv"
        if sample_path.exists():
            return self.parse_csv_file(sample_path)
        return []
