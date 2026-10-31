"""
CPCB (Central Pollution Control Board) Data Connector.
Primary portal: https://cpcb.nic.in/
CCR Portal: https://app.cpcbccr.com/
Continuous Ambient Air Quality Monitoring (CAAQMS) network.
"""

import csv
import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.config import (
    CPCB_CCR_URL, CPCB_MAIN_URL, DATA_DIR,
    PROVENANCE_DIRECT, PROVENANCE_HISTORICAL
)
from backend.connectors.base_connector import BaseGovernmentConnector
from backend.aqi_calculator import calculate_cpcb_aqi

logger = logging.getLogger("diwali_airwatch.cpcb_connector")

class CPCBConnector(BaseGovernmentConnector):
    def __init__(self):
        super().__init__(
            name="CPCB_CAAQMS_Connector",
            source_url="https://app.cpcbccr.com/ccr/#/caaqms-dashboard-cpcb",
            department="Central Pollution Control Board, MoEFCC"
        )
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
        Attempts to query official CPCB CCR portal endpoints.
        If live portal is protected by Cloudflare/WAF or offline,
        gracefully reports status and falls back to verified official CPCB records.
        """
        api_endpoint = "https://app.cpcbccr.com/caaqms/caaqms_landing_map_all"
        logger.info(f"[{self.name}] Connecting to CPCB CCR endpoint: {api_endpoint}")

        response = self.make_http_request(api_endpoint, max_retries=2)

        if response and response.status_code == 200:
            try:
                data = response.json()
                parsed_records = self._parse_cpcb_json(data)
                return {
                    "status": "SUCCESS",
                    "records": parsed_records,
                    "source_url": self.source_url,
                    "provenance": PROVENANCE_DIRECT,
                    "retrieval_time": datetime.utcnow().isoformat(),
                    "message": f"Successfully retrieved {len(parsed_records)} live observations from CPCB CCR portal."
                }
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to parse live JSON from CPCB: {e}")

        # If live source is unavailable (common in sandboxed or firewalled environments)
        logger.info(f"[{self.name}] CPCB live portal unreachable. Loading official CPCB archival records.")
        fallback_records = self._load_recent_archival_records()
        
        return {
            "status": "SOURCE_UNAVAILABLE",
            "fallback_used": True,
            "records": fallback_records,
            "source_url": "https://cpcb.nic.in/official-ambient-air-quality-bulletin",
            "provenance": PROVENANCE_HISTORICAL,
            "retrieval_time": datetime.utcnow().isoformat(),
            "message": "Official CPCB CCR live portal is currently inaccessible. Serving verified official CPCB archival observations with full provenance."
        }

    def _parse_cpcb_json(self, data: Any) -> List[Dict[str, Any]]:
        """
        Parses raw CPCB CAAQMS map/landing API response.
        """
        records = []
        now = datetime.utcnow()
        # Handle dict or list format returned by CAAQMS map
        station_list = data if isinstance(data, list) else data.get("stations", data.get("data", []))

        for st in station_list:
            st_id = st.get("id") or st.get("station_id") or st.get("site_id")
            if not st_id:
                continue

            pollutants = {
                "pm25": st.get("pm25") or st.get("PM2.5"),
                "pm10": st.get("pm10") or st.get("PM10"),
                "no2": st.get("no2") or st.get("NO2"),
                "so2": st.get("so2") or st.get("SO2"),
                "co": st.get("co") or st.get("CO"),
                "o3": st.get("o3") or st.get("OZONE"),
            }

            aqi_res = calculate_cpcb_aqi(pollutants)

            records.append({
                "station_id": str(st_id),
                "station_name": st.get("site_name", "CPCB Station"),
                "observation_time": now,
                "pm25": pollutants["pm25"],
                "pm10": pollutants["pm10"],
                "no2": pollutants["no2"],
                "so2": pollutants["so2"],
                "co": pollutants["co"],
                "o3": pollutants["o3"],
                "cpcb_aqi": aqi_res["aqi"],
                "prominent_pollutant": aqi_res["prominent_pollutant"],
                "aqi_category": aqi_res["category"],
                "source_name": "CPCB CAAQMS CCR Portal",
                "source_url": self.source_url,
                "retrieval_time": now,
                "provenance": PROVENANCE_DIRECT,
                "dedup_hash": self.compute_dedup_hash(str(st_id), now, "CPCB_LIVE")
            })

        return records

    def parse_csv_file(self, file_path_or_content: Any) -> List[Dict[str, Any]]:
        """
        Parses officially downloaded CPCB CSV data (e.g. from app.cpcbccr.com report download).
        Columns typically: Station, Date, PM2.5 (ug/m3), PM10 (ug/m3), NO2 (ug/m3), SO2 (ug/m3), CO (mg/m3), Ozone (ug/m3)...
        """
        records = []
        if isinstance(file_path_or_content, (str, Path)) and Path(file_path_or_content).exists():
            with open(file_path_or_content, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                records = self._parse_csv_dict_reader(reader)
        elif isinstance(file_path_or_content, str):
            reader = csv.DictReader(io.StringIO(file_path_or_content))
            records = self._parse_csv_dict_reader(reader)

        logger.info(f"[{self.name}] Parsed {len(records)} records from official CPCB CSV export.")
        return records

    def _parse_csv_dict_reader(self, reader: csv.DictReader) -> List[Dict[str, Any]]:
        records = []
        now = datetime.utcnow()

        for row in reader:
            st_name = row.get("Station") or row.get("station") or row.get("Station Name") or "Unknown CPCB Station"
            date_str = row.get("Date") or row.get("timestamp") or row.get("From Date") or now.strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                obs_dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M:%S")
            except Exception:
                try:
                    obs_dt = datetime.fromisoformat(date_str.strip())
                except Exception:
                    obs_dt = now

            def safe_float(key_patterns):
                for k in row:
                    if not k:
                        continue
                    for pat in key_patterns:
                        if pat.lower() in str(k).lower():
                            try:
                                return float(row[k])
                            except (ValueError, TypeError):
                                pass
                return None

            pm25 = safe_float(["pm2.5", "pm25"])
            pm10 = safe_float(["pm10"])
            no2 = safe_float(["no2"])
            so2 = safe_float(["so2"])
            co = safe_float(["co"])
            o3 = safe_float(["ozone", "o3"])

            # Match station_id from metadata if possible
            st_id = "CPCB_CUSTOM"
            for meta in self.stations_metadata:
                m_name = meta.get("name", "")
                if m_name and st_name and (m_name.lower() in st_name.lower() or st_name.lower() in m_name.lower()):
                    st_id = meta["station_id"]
                    break

            aqi_res = calculate_cpcb_aqi({"pm25": pm25, "pm10": pm10, "no2": no2, "so2": so2, "co": co, "o3": o3})

            records.append({
                "station_id": st_id,
                "station_name": st_name,
                "observation_time": obs_dt,
                "pm25": pm25,
                "pm10": pm10,
                "no2": no2,
                "so2": so2,
                "co": co,
                "o3": o3,
                "cpcb_aqi": aqi_res["aqi"],
                "prominent_pollutant": aqi_res["prominent_pollutant"],
                "aqi_category": aqi_res["category"],
                "source_name": "Official CPCB Downloaded CSV",
                "source_url": "https://app.cpcbccr.com/ccr/#/caaqms-dashboard-cpcb",
                "retrieval_time": now,
                "provenance": "OFFICIAL_CSV_IMPORT",
                "dedup_hash": self.compute_dedup_hash(st_id, obs_dt, "CPCB_CSV")
            })

        return records

    def _load_recent_archival_records(self) -> List[Dict[str, Any]]:
        """
        Reads the latest records from the verified CPCB historical dataset.
        """
        hist_path = DATA_DIR / "historical_cpcb_diwali_data.csv"
        records = []
        if not hist_path.exists():
            return []

        now = datetime.utcnow()
        with open(hist_path, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            # Pick latest 30 records
            recent_slice = reader[-30:]
            for row in recent_slice:
                try:
                    obs_dt = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
                except Exception:
                    obs_dt = now

                pm25 = float(row["pm25"]) if row.get("pm25") else None
                pm10 = float(row["pm10"]) if row.get("pm10") else None
                no2 = float(row["no2"]) if row.get("no2") else None
                so2 = float(row["so2"]) if row.get("so2") else None
                co = float(row["co"]) if row.get("co") else None
                o3 = float(row["o3"]) if row.get("o3") else None

                aqi_res = calculate_cpcb_aqi({"pm25": pm25, "pm10": pm10, "no2": no2, "so2": so2, "co": co, "o3": o3})

                records.append({
                    "station_id": row["station_id"],
                    "station_name": row["station_name"],
                    "city": row["city"],
                    "observation_time": obs_dt,
                    "pm25": pm25,
                    "pm10": pm10,
                    "no2": no2,
                    "so2": so2,
                    "co": co,
                    "o3": o3,
                    "cpcb_aqi": aqi_res["aqi"],
                    "prominent_pollutant": aqi_res["prominent_pollutant"],
                    "aqi_category": aqi_res["category"],
                    "source_name": "CPCB CAAQMS Historical Bulletin",
                    "source_url": "https://cpcb.nic.in/National-Air-Quality-Index/",
                    "retrieval_time": now,
                    "provenance": PROVENANCE_HISTORICAL,
                    "dedup_hash": self.compute_dedup_hash(row["station_id"], obs_dt, "CPCB_HIST")
                })

        return records
