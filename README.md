# 🌬️ AetherQI – Intelligent Air. Predictive Insights.

> **Official Government of India Air Quality Intelligence, Multi-City Predictive Modeling, and Open Data Architecture.**  
> *Developed for Environmental Intelligence, Scenario Simulation, and Real-Time Air Shed Forecasting.*

---

## 🏛️ 1. Executive Summary & Mission

**AetherQI** is a scientifically grounded air quality monitoring, geospatial visualization, and predictive intelligence platform. It provides high-resolution neighbourhood air quality analysis across key Indian urban regions including **Ludhiana (Punjab)**, **Delhi (National Capital Territory)**, and **Chandigarh (Union Territory)**.

The platform integrates official Government of India (GoI) data sources and regulatory standards:
1. **Central Pollution Control Board (CPCB)**
2. **Open Government Data Platform (data.gov.in)**
3. **India Meteorological Department (IMD)**
4. **Ministry of Environment, Forest and Climate Change (MoEFCC)**
5. **Ministry of Road Transport and Highways (MoRTH)**

### Core Philosophical Mandate:
- **No Fabricated Readings**: Synthetic or demonstration data is **never** presented as real-time government readings.
- **Strict Data Provenance**: Every observation displays its originating government department, station ID, coordinates, observation timestamp, last-updated timestamp, and a visible provenance badge (`DIRECTLY_MEASURED`, `SPATIALLY_ESTIMATED`, `MODEL_PREDICTED`, `HISTORICAL_GOVERNMENT_RECORD`, or `SIMULATED_PREDICTION`).
- **Standard-Compliant AQI**: Implements the official **CPCB IND-AQI piecewise linear sub-index methodology**. In strict compliance with CPCB regulations, overall AQI is calculated **only** when at least 3 pollutants are monitored (with PM2.5 or PM10 present) and is **never** calculated from PM2.5 alone.
- **Multi-City Isolation**: Complete data segregation between cities (Ludhiana, Delhi, Chandigarh) with distinct geographic coordinates, monitoring stations, meteorological parameters, and neighbourhood typologies.

---

## 🌐 2. Official Government Data Sources

| Department / Agency | Official Website | Integrated Services & Datasets | Official URL / API Reference |
| :--- | :--- | :--- | :--- |
| **Central Pollution Control Board (CPCB)** | [cpcb.nic.in](https://cpcb.nic.in/) | CAAQMS continuous ambient air monitoring stations, pollutant concentrations (PM2.5, PM10, NO2, SO2, CO, O3, NH3). | [CPCB CCR Portal](https://app.cpcbccr.com/ccr/#/caaqms-dashboard-cpcb) |
| **National Informatics Centre (NIC) / data.gov.in** | [data.gov.in](https://www.data.gov.in/) | Real-time Air Quality Index catalog, daily city-wide observation aggregates. | [data.gov.in Real-Time AQI](https://www.data.gov.in/catalog/real-time-air-quality-index) |
| **India Meteorological Department (IMD)** | [mausam.imd.gov.in](https://mausam.imd.gov.in/) | Surface observatories, ambient temperature, relative humidity, wind speed, wind direction, rainfall. | [IMD API Portal](https://api.imd.gov.in/public/index.php) |
| **Ministry of Environment, Forest & Climate Change** | [moef.gov.in](https://moef.gov.in/) | National Ambient Air Quality Standards (NAAQS) and IND-AQI Technical Report. | [CPCB National AQI](https://cpcb.nic.in/National-Air-Quality-Index/) |
| **Ministry of Road Transport & Highways (MoRTH)** | [morth.nic.in](https://morth.nic.in/) | Road Transport Year Book, highway corridor freight indices, Smart Cities Mission urban transit density benchmarks. | [MoRTH Transport Data](https://morth.nic.in/road-transport-year-book) |

---

## 🗺️ 3. Interactive Leaflet GIS Map

- **Zero-Failure Local Assets**: Leaflet CSS and JS are bundled locally with zero CDN external downtime risk.
- **Dual Map Basemaps**:
  - **Light Theme**: CartoDB Positron / OSM Light tile layer.
  - **Dark Theme**: CartoDB Dark Matter / Alidade Smooth Dark tile layer.
- **Multi-City Navigation**: Seamless map centering, zooming, and marker repositioning when switching between Ludhiana, Delhi, and Chandigarh.
- **Dynamic Hotspots**: Circular markers sized and colored according to CPCB IND-AQI category bands (Good, Satisfactory, Moderate, Poor, Very Poor, Severe).
- **11-Day Time-Lapse Player**: Interactive timeline slider (-5 to +5 days) with automated Play/Pause animation.

---

## 🌓 4. Dual Theme System (Light & Dark)

- **Default Light Theme**: Pure white (`#FFFFFF`), light blue accents (`#60A5FA`, `#EFF6FF`), dark charcoal text (`#111827`), slate grey (`#64748B`), and subtle borders (`#E2E8F0`).
- **Enterprise Dark Theme**: Midnight blue background (`#0F172A`, `#111C30`), card containers (`#172337`), high-contrast text (`#F8FAFC`, `#A7B4C7`), dark blue highlights (`#1E3A5F`), and dark borders (`#334155`).
- **Instant Toggle & Persistence**: Sun/Moon toggle in the navigation bar with `localStorage` persistence and `prefers-color-scheme` support.

---

## 🚀 5. Running the Application

### 1. Start the FastAPI Backend & Static Server
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in any modern browser.

### 2. Run the Automated Test Suite
```powershell
.\.venv\Scripts\python.exe -m pytest tests/
```
All 33 unit and integration tests verify:
- API endpoints (simulation, timeline, heatmap, predictions, alerts, neighbourhoods)
- Multi-pollutant CPCB AQI calculation
- Location mapping & Haversine proximity calculations
- Random Forest ML scenario predictions and confidence intervals
- Data ingestion connectors and CSV uploads
