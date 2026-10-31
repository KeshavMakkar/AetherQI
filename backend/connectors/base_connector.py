"""
Base Connector for Government Data Sources.
Provides:
- Standardized request handling with configurable retries and timeout
- Response validation and unit normalization
- Deduplication hash generation: sha256(station_id + timestamp + source)
- Ingestion logging and error audit trails
"""

import hashlib
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
from backend.config import REQUEST_TIMEOUT_SECONDS, MAX_RETRIES

logger = logging.getLogger("diwali_airwatch.connector")
logging.basicConfig(level=logging.INFO)

class BaseGovernmentConnector(ABC):
    def __init__(self, name: str, source_url: str, department: str):
        self.name = name
        self.source_url = source_url
        self.department = department

    def compute_dedup_hash(self, station_id: str, obs_time: datetime, source_tag: str) -> str:
        """
        Generates unique SHA-256 hash to prevent duplicate entries in database.
        """
        raw = f"{station_id}_{obs_time.strftime('%Y%m%d%H%M%S')}_{source_tag}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def make_http_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = REQUEST_TIMEOUT_SECONDS,
        max_retries: int = MAX_RETRIES
    ) -> Optional[requests.Response]:
        """
        Robust HTTP request with exponential backoff retry.
        Respects government server rate limits and logs all connection attempts.
        """
        attempt = 0
        backoff = 1.0

        default_headers = {
            "User-Agent": "DiwaliAirWatch-AcademicResearch/1.0 (GovtDataIngestion/Python)"
        }
        if headers:
            default_headers.update(headers)

        while attempt < max_retries:
            attempt += 1
            try:
                logger.info(f"[{self.name}] Attempt {attempt}/{max_retries} connecting to {url}")
                response = requests.get(url, params=params, headers=default_headers, timeout=timeout)
                
                if response.status_code == 200:
                    return response
                elif response.status_code in (401, 403):
                    logger.warning(f"[{self.name}] Authentication required or forbidden (HTTP {response.status_code})")
                    return response
                elif response.status_code in (429, 500, 502, 503, 504):
                    logger.warning(f"[{self.name}] Server responded with status {response.status_code}. Backing off {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    logger.error(f"[{self.name}] Unexpected response HTTP {response.status_code}: {response.text[:200]}")
                    return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"[{self.name}] Request failed (attempt {attempt}): {e}")
                time.sleep(backoff)
                backoff *= 2.0

        logger.error(f"[{self.name}] All {max_retries} attempts to {url} failed.")
        return None

    @abstractmethod
    def fetch_live_data(self) -> Dict[str, Any]:
        """
        Fetch data from the live government endpoint.
        Returns dict with keys: 'status', 'records', 'source_url', 'error_message', 'provenance'
        """
        pass

    @abstractmethod
    def parse_csv_file(self, file_path_or_content: Any) -> List[Dict[str, Any]]:
        """
        Parse officially downloaded CSV files from this government source.
        """
        pass

