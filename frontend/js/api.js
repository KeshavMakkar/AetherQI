/**
 * AetherQI API Client
 * Official Government Data Integration & Multi-City Predictive Air Quality Intelligence.
 * Supports AbortController signal handling to prevent race conditions during rapid location switching.
 */

const API_BASE = "";

export async function fetchStations(signal) {
  const res = await fetch(`${API_BASE}/api/stations`, { signal });
  if (!res.ok) throw new Error("Failed to load monitoring stations");
  return await res.json();
}

export async function fetchCities(signal) {
  const res = await fetch(`${API_BASE}/api/cities`, { signal });
  if (!res.ok) throw new Error("Failed to load cities registry");
  return await res.json();
}

export async function fetchNeighbourhoods(city = "", signal) {
  const url = `${API_BASE}/api/neighbourhoods${city && city.toLowerCase() !== "all" ? `?city=${encodeURIComponent(city)}` : ""}`;
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error("Failed to load neighbourhoods");
  return await res.json();
}

export async function fetchLatestAirQuality(city = "", limit = 50, signal) {
  const url = `${API_BASE}/api/air-quality/latest?limit=${limit}${city && city.toLowerCase() !== "all" ? `&city=${encodeURIComponent(city)}` : ""}`;
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error("Failed to load air quality observations");
  return await res.json();
}

export async function fetchWeather(city = "", signal) {
  const url = `${API_BASE}/api/weather/latest${city && city.toLowerCase() !== "all" ? `?city=${encodeURIComponent(city)}` : ""}`;
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error("Failed to load weather observations");
  return await res.json();
}

export async function fetchTransport(signal) {
  const res = await fetch(`${API_BASE}/api/transport/latest`, { signal });
  if (!res.ok) throw new Error("Failed to load transport indicators");
  return await res.json();
}

export async function predictAirQuality(location, scenario, hoursAhead = 24, signal) {
  const res = await fetch(`${API_BASE}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      neighbourhood_or_station: location,
      scenario: scenario,
      hours_ahead: hoursAhead
    }),
    signal
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Prediction request failed");
  }
  return await res.json();
}

export async function fetchDataSourcesSummary(signal) {
  const res = await fetch(`${API_BASE}/api/data-sources`, { signal });
  if (!res.ok) throw new Error("Failed to load data governance summary");
  return await res.json();
}

export async function fetchMLMetrics(signal) {
  const res = await fetch(`${API_BASE}/api/ml/metrics`, { signal });
  if (!res.ok) throw new Error("Failed to load ML model metrics");
  return await res.json();
}

export async function triggerIngestion(signal) {
  const res = await fetch(`${API_BASE}/api/ingest/trigger`, { method: "POST", signal });
  if (!res.ok) throw new Error("Failed to trigger automated ingestion");
  return await res.json();
}

export async function uploadCustomCSV(fileContent, sourceType = "cpcb", signal) {
  const res = await fetch(`${API_BASE}/api/ingest/upload-csv`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      file_content: fileContent,
      source_type: sourceType
    }),
    signal
  });
  if (!res.ok) throw new Error("Failed to upload custom CSV dataset");
  return await res.json();
}

// ----------------- MULTI-CITY HEURISTIC SIMULATION ENDPOINTS ----------------- //

export async function fetchFestivalConfig(signal) {
  const res = await fetch(`${API_BASE}/api/festival-config`, { signal });
  if (!res.ok) throw new Error("Failed to load central festival configuration");
  return await res.json();
}

export async function fetchSimulation(city = "Delhi", signal) {
  const url = `${API_BASE}/api/simulation?city=${encodeURIComponent(city)}`;
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error(`Failed to load simulation dataset for ${city}`);
  return await res.json();
}

export async function fetchSimulationTimeline(city = "Delhi", signal) {
  const url = `${API_BASE}/api/simulation/timeline?city=${encodeURIComponent(city)}`;
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error(`Failed to load simulation timeline for ${city}`);
  return await res.json();
}

export async function fetchHeatmap(city = "Delhi", dayOffset = 0, hour = 20, signal) {
  const url = `${API_BASE}/api/heatmap?city=${encodeURIComponent(city)}&day_offset=${dayOffset}&hour=${hour}`;
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error(`Failed to load heatmap data for ${city}`);
  return await res.json();
}

export async function fetchPredictions(city = "Delhi", neighbourhood = "", signal) {
  let url = `${API_BASE}/api/predictions?city=${encodeURIComponent(city)}`;
  if (neighbourhood && neighbourhood.toLowerCase() !== "all") {
    url += `&neighbourhood=${encodeURIComponent(neighbourhood)}`;
  }
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error(`Failed to load prediction curves for ${city}`);
  return await res.json();
}

export async function fetchAlerts(city = "Delhi", severity = "", neighbourhood = "", signal) {
  let url = `${API_BASE}/api/alerts?city=${encodeURIComponent(city)}&`;
  if (severity) url += `severity=${encodeURIComponent(severity)}&`;
  if (neighbourhood && neighbourhood.toLowerCase() !== "all") {
    url += `&neighbourhood=${encodeURIComponent(neighbourhood)}`;
  }
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error(`Failed to load actionable alerts for ${city}`);
  return await res.json();
}
