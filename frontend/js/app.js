/**
 * AetherQI – Intelligent Air. Predictive Insights.
 * Main Application Controller & Global State Synchronization Engine
 */

import {
  fetchStations,
  fetchCities,
  fetchNeighbourhoods,
  fetchLatestAirQuality,
  fetchWeather,
  fetchTransport,
  predictAirQuality,
  fetchDataSourcesSummary,
  fetchMLMetrics,
  triggerIngestion,
  uploadCustomCSV,
  fetchFestivalConfig,
  fetchSimulation,
  fetchSimulationTimeline,
  fetchHeatmap,
  fetchPredictions,
  fetchAlerts,
  fetchMapsConfig
} from "./api.js";

import {
  setupGoogleMapsHeatmap,
  updateGoogleMapsTheme,
  panGoogleMapsToCity,
  focusGoogleMapsNeighbourhood,
  refreshGoogleMapsOverlays,
  onGoogleMapsError
} from "./google_maps.js";

import {
  renderPredictionTimelineChart,
  renderForecastChart,
  renderFeatureImportance
} from "./charts.js";

// =============================================================================
// CENTRAL APPLICATION STATE & STORE (TASK 2 & 6)
// =============================================================================

const CITY_COORDINATES = {
  // 8 Primary Metropolitan Cities
  "Delhi": { lat: 28.6139, lng: 77.2090, zoom: 12, state: "Delhi (NCT)", station: "Anand Vihar, Delhi - DPCC Live CAAQMS" },
  "Mumbai": { lat: 19.0760, lng: 72.8777, zoom: 12, state: "Maharashtra", station: "Bandra Kurla Complex (BKC), Mumbai - MPCB" },
  "Bengaluru": { lat: 12.9716, lng: 77.5946, zoom: 12, state: "Karnataka", station: "BTM Layout, Bengaluru - KSPCB" },
  "Hyderabad": { lat: 17.3850, lng: 78.4867, zoom: 12, state: "Telangana", station: "Sanathnagar, Hyderabad - TSPCB" },
  "Kolkata": { lat: 22.5726, lng: 88.3639, zoom: 12, state: "West Bengal", station: "Victoria Memorial, Kolkata - WBPCB" },
  "Chennai": { lat: 13.0827, lng: 80.2707, zoom: 12, state: "Tamil Nadu", station: "Alandur Bus Depot, Chennai - TNPCB" },
  "Pune": { lat: 18.5204, lng: 73.8567, zoom: 12, state: "Maharashtra", station: "Shivajinagar, Pune - MPCB" },
  "Ahmedabad": { lat: 23.0225, lng: 72.5714, zoom: 12, state: "Gujarat", station: "Maninagar, Ahmedabad - GPCB" },

  // 12 Additional Metropolitan & Industrial Cities
  "Jaipur": { lat: 26.9124, lng: 75.7873, zoom: 12, state: "Rajasthan", station: "Adarsh Nagar, Jaipur - RSPCB" },
  "Lucknow": { lat: 26.8467, lng: 80.9462, zoom: 12, state: "Uttar Pradesh", station: "Talkatora District Industries Center, Lucknow - UPPCB" },
  "Ludhiana": { lat: 30.9010, lng: 75.8573, zoom: 12, state: "Punjab", station: "Punjab Agricultural University (PAU), Ludhiana - PPCB" },
  "Chandigarh": { lat: 30.7333, lng: 76.7794, zoom: 12, state: "Chandigarh (UT)", station: "Sector 22, Chandigarh - CPCC" },
  "Bhopal": { lat: 23.2599, lng: 77.4126, zoom: 12, state: "Madhya Pradesh", station: "T.T. Nagar, Bhopal - MPPCB" },
  "Indore": { lat: 22.7196, lng: 75.8577, zoom: 12, state: "Madhya Pradesh", station: "Chhoti Gwaltoli, Indore - MPPCB" },
  "Surat": { lat: 21.1702, lng: 72.8311, zoom: 12, state: "Gujarat", station: "Varachha, Surat - GPCB" },
  "Nagpur": { lat: 21.1458, lng: 79.0882, zoom: 12, state: "Maharashtra", station: "Civil Lines, Nagpur - MPCB" },
  "Patna": { lat: 25.5941, lng: 85.1376, zoom: 12, state: "Bihar", station: "DRM Office Danapur, Patna - BSPCB" },
  "Kanpur": { lat: 26.4499, lng: 80.3319, zoom: 12, state: "Uttar Pradesh", station: "Nehru Nagar, Kanpur - UPPCB" },
  "Kochi": { lat: 9.9312, lng: 76.2673, zoom: 12, state: "Kerala", station: "Vyttila, Kochi - KPCB" },
  "Bhubaneswar": { lat: 20.2961, lng: 85.8245, zoom: 12, state: "Odisha", station: "IRC Village, Bhubaneswar - OSPCB" }
};

class CentralStateStore {
  constructor() {
    this.city = localStorage.getItem("aetherqi_default_city") || "Delhi";
    this.neighbourhood = "all";
    this.dayOffset = 0;
    this.dateRange = "all";
    this.aqiFilter = "all";
    this.dataSourceFilter = "all";
    this.theme = localStorage.getItem("aetherqi_theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    this.festivalConfig = null;
    this.simulationData = null;
    this.timelineMilestones = [];
    this.predictionCurves = [];
    this.alerts = [];
    this.weather = null;
    this.mapsConfig = null;
    this.citiesList = [];
    this.abortController = null;
    this.subscribers = [];
  }

  subscribe(callback) {
    this.subscribers.push(callback);
    return () => {
      this.subscribers = this.subscribers.filter(s => s !== callback);
    };
  }

  notify(event, payload) {
    this.subscribers.forEach(s => s(event, payload, this));
  }

  setTheme(newTheme) {
    this.theme = newTheme;
    localStorage.setItem("aetherqi_theme", newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
    this.notify("THEME_CHANGED", newTheme);
  }

  setCity(newCity) {
    if (this.city === newCity) return;
    this.city = newCity;
    this.neighbourhood = "all";
    this.notify("CITY_CHANGED", newCity);
  }

  setNeighbourhood(nh) {
    this.neighbourhood = nh;
    this.notify("NEIGHBOURHOOD_CHANGED", nh);
  }

  setDayOffset(offset) {
    this.dayOffset = offset;
    this.notify("TIMELINE_CHANGED", offset);
  }

  setDateRange(range) {
    this.dateRange = range;
    this.notify("DATE_RANGE_CHANGED", range);
  }

  setAqiFilter(filter) {
    this.aqiFilter = filter;
    this.notify("AQI_FILTER_CHANGED", filter);
  }

  setDataSourceFilter(source) {
    this.dataSourceFilter = source;
    this.notify("DATA_SOURCE_FILTER_CHANGED", source);
  }
}

const store = new CentralStateStore();

// Playback and Map State
let playbackTimer = null;
let isPlaying = false;

// Helpers: AQI Colors
function getAQIColor(aqi) {
  if (aqi === null || aqi === undefined) return "#64748B";
  if (aqi <= 50) return "#10B981";       // Good
  if (aqi <= 100) return "#84CC16";      // Satisfactory
  if (aqi <= 200) return "#EAB308";      // Moderate
  if (aqi <= 300) return "#F97316";      // Poor
  if (aqi <= 400) return "#EF4444";      // Very Poor
  return "#991B1B";                      // Severe
}

function getAQICategory(aqi) {
  if (aqi <= 50) return "Good";
  if (aqi <= 100) return "Satisfactory";
  if (aqi <= 200) return "Moderate";
  if (aqi <= 300) return "Poor";
  if (aqi <= 400) return "Very Poor";
  return "Severe";
}

function refreshIcons() {
  if (window.lucide && typeof window.lucide.createIcons === "function") {
    window.lucide.createIcons();
  }
}

// =============================================================================
// LIFECYCLE & INITIALIZATION
// =============================================================================

document.addEventListener("DOMContentLoaded", async () => {
  // Apply saved theme immediately
  document.documentElement.setAttribute("data-theme", store.theme);
  updateThemeIcon(store.theme);

  setupThemeToggle();
  setupNavigationTabs();
  setupTopBarControls();
  setupSettingsTab();
  setupModals();
  setupTimelinePlayback();
  setupSimulationForm();

  // Load Google Maps API configuration from backend
  try {
    store.mapsConfig = await fetchMapsConfig();
  } catch (err) {
    console.warn("Unable to fetch maps configuration:", err);
    store.mapsConfig = { configured: false, api_key: null, env_var_name: "GOOGLE_MAPS_API_KEY" };
  }

  // Subscribe to Google Maps authentication/network failures
  onGoogleMapsError((type, details) => {
    console.warn("Google Maps error event intercepted:", type, details);
    initInteractiveMap();
    initDedicatedHeatmap();
  });

  // Load initial city data (also initializes Google Maps)
  await loadCityData(store.city);

  refreshIcons();
});

// =============================================================================
// TASK 4: DARK MODE & THEME CONTROLLER
// =============================================================================

function setupThemeToggle() {
  const btn = document.getElementById("themeToggleBtn");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const nextTheme = store.theme === "dark" ? "light" : "dark";
    store.setTheme(nextTheme);
    updateThemeIcon(nextTheme);

    // Synchronize Google Maps dark/light mode palette
    updateGoogleMapsTheme(nextTheme);

    // Re-render heatmap markers with updated theme popups
    renderHeatmapMarkers(store.dayOffset);

    // Re-render chart for dark/light gridline colors
    renderFilteredPredictionChart();

    refreshIcons();
  });
}

function updateThemeIcon(theme) {
  const btn = document.getElementById("themeToggleBtn");
  if (btn) {
    btn.innerHTML = `<i data-lucide="${theme === 'dark' ? 'moon' : 'sun'}" id="themeIcon" style="width: 18px; height: 18px;"></i>`;
  }
  const radioLight = document.getElementById("themeRadioLight");
  const radioDark = document.getElementById("themeRadioDark");
  if (radioLight && radioDark) {
    if (theme === "dark") {
      radioDark.checked = true;
    } else {
      radioLight.checked = true;
    }
  }
  refreshIcons();
}

// =============================================================================
// GOOGLE MAPS JAVASCRIPT API CONTROLLER & FALLBACK HANDLERS
// =============================================================================

async function initInteractiveMap() {
  const cityCfg = CITY_COORDINATES[store.city] || CITY_COORDINATES["Delhi"];
  await setupGoogleMapsHeatmap({
    containerId: "aetherqiHeatmap",
    city: store.city,
    cityCoords: cityCfg,
    simulationData: store.simulationData,
    dayOffset: store.dayOffset,
    aqiFilter: store.aqiFilter,
    theme: store.theme,
    backendConfig: store.mapsConfig
  });
}

async function initDedicatedHeatmap() {
  const cityCfg = CITY_COORDINATES[store.city] || CITY_COORDINATES["Delhi"];
  await setupGoogleMapsHeatmap({
    containerId: "dedicatedHeatmapView",
    city: store.city,
    cityCoords: cityCfg,
    simulationData: store.simulationData,
    dayOffset: store.dayOffset,
    aqiFilter: store.aqiFilter,
    theme: store.theme,
    backendConfig: store.mapsConfig
  });
}

function renderHeatmapMarkers(dayOffset) {
  refreshGoogleMapsOverlays(store.simulationData, dayOffset, store.aqiFilter, store.theme);
}

function panMapToCity(city) {
  const cityCfg = typeof city === "string" ? (CITY_COORDINATES[city] || CITY_COORDINATES["Delhi"]) : city;
  panGoogleMapsToCity(cityCfg);
}

function focusNeighbourhoodOnMap(name) {
  if (!name || name === "all") {
    panMapToCity(store.city);
    return;
  }
  focusGoogleMapsNeighbourhood(name, store.simulationData, store.theme);
}

// =============================================================================
// TASK 2: LOCATION SWITCHING & DATA FETCHING WITH ABORTCONTROLLER
// =============================================================================

function updateAiSimulationLocations(neighbourhoods) {
  const locSelect = document.getElementById("aiSimLocation");
  if (!locSelect || !neighbourhoods || neighbourhoods.length === 0) return;
  locSelect.innerHTML = neighbourhoods.map(n => `
    <option value="${n.name}">${n.name} (${n.city || store.city})</option>
  `).join("");
}

async function loadCityData(city) {
  // Normalize target city
  const targetCity = (typeof city === "string" && city.trim()) ? city.trim() : "Delhi";
  let matchedCity = "Delhi";
  for (const k of Object.keys(CITY_COORDINATES)) {
    if (k.toLowerCase() === targetCity.toLowerCase()) {
      matchedCity = k;
      break;
    }
  }

  store.city = matchedCity;
  store.neighbourhood = "all";

  // Cancel previous pending requests to prevent race conditions
  if (store.abortController) {
    store.abortController.abort();
  }
  store.abortController = new AbortController();
  const signal = store.abortController.signal;

  showLoadingState();

  try {
    const [festivalCfg, simRes, timelineRes, predsRes, alertsRes, weatherRes, govRes] = await Promise.all([
      fetchFestivalConfig(signal).catch(() => ({})),
      fetchSimulation(matchedCity, signal),
      fetchSimulationTimeline(matchedCity, signal),
      fetchPredictions(matchedCity, "all", signal),
      fetchAlerts(matchedCity, "", "", signal),
      fetchWeather(matchedCity, signal).catch(() => []),
      fetchDataSourcesSummary(signal).catch(() => ({}))
    ]);

    store.festivalConfig = festivalCfg;
    store.simulationData = simRes;
    store.timelineMilestones = timelineRes;
    store.predictionCurves = predsRes;
    store.alerts = alertsRes;
    store.weather = weatherRes && weatherRes.length > 0 ? weatherRes[0] : null;

    // Update Header City Title
    const headerTitle = document.getElementById("headerCityTitle");
    if (headerTitle) {
      headerTitle.textContent = `${matchedCity} Air Quality Intelligence`;
    }

    // Update Active Station Pill
    const stationPill = document.getElementById("activeStationPill");
    const cityCfg = CITY_COORDINATES[matchedCity] || CITY_COORDINATES["Delhi"];
    if (stationPill) {
      stationPill.textContent = simRes?.metadata?.station_name || cityCfg.station;
    }

    // Sync Global City Selector if needed
    const citySelector = document.getElementById("globalCitySelector");
    if (citySelector && citySelector.value !== matchedCity) {
      citySelector.value = matchedCity;
    }

    // Populate Dynamic Controls
    populateNeighbourhoodDropdown(simRes?.neighbourhoods);
    populateDateDropdown(store.timelineMilestones);
    updateAiSimulationLocations(simRes?.neighbourhoods);

    // Render Components
    renderFilteredPredictionChart();
    renderNeighbourhoodCards(simRes?.neighbourhoods);
    renderAlertsList(store.alerts);
    renderGovernanceTables(govRes);
    renderTimelineTab(store.timelineMilestones);
    renderEnvironmentTab(simRes, store.weather);

    // Pan map to new city and plot Google Maps markers/overlays
    await setupGoogleMapsHeatmap({
      containerId: "aetherqiHeatmap",
      city: matchedCity,
      cityCoords: cityCfg,
      simulationData: simRes,
      dayOffset: store.dayOffset,
      aqiFilter: store.aqiFilter,
      theme: store.theme,
      backendConfig: store.mapsConfig
    });
    panGoogleMapsToCity(cityCfg);

    // Synchronize dedicated heatmap view if currently visible
    const dedicatedEl = document.getElementById("dedicatedHeatmapView");
    if (dedicatedEl && dedicatedEl.offsetParent !== null) {
      setupGoogleMapsHeatmap({
        containerId: "dedicatedHeatmapView",
        city: matchedCity,
        cityCoords: cityCfg,
        simulationData: simRes,
        dayOffset: store.dayOffset,
        aqiFilter: store.aqiFilter,
        theme: store.theme,
        backendConfig: store.mapsConfig
      });
    }

    // Update metrics for current day offset
    updateDashboardMetricsForOffset(store.dayOffset);

    // Update Last Updated Timestamp
    const timeEl = document.getElementById("lastUpdatedText");
    if (timeEl) {
      const now = new Date();
      timeEl.textContent = `Updated: ${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    }

    hideLoadingState();
    refreshIcons();
  } catch (err) {
    if (err.name === "AbortError") {
      console.log("Request aborted for previous city");
      return;
    }
    console.error("Location Data Load Error:", err);
    hideLoadingState();
  }
}

function showLoadingState() {
  const cards = document.querySelectorAll(".summary-card, .nh-card");
  cards.forEach(c => c.style.opacity = "0.6");
}

function hideLoadingState() {
  const cards = document.querySelectorAll(".summary-card, .nh-card");
  cards.forEach(c => c.style.opacity = "1");
}

function getFilteredPredictionCurves() {
  if (!store.predictionCurves || store.predictionCurves.length === 0) return [];
  if (store.dateRange === "all") return store.predictionCurves;

  return store.predictionCurves.map(curve => {
    let filteredPoints = curve.points;
    if (store.dateRange === "pre") {
      filteredPoints = curve.points.filter(p => p.day_offset < 0);
    } else if (store.dateRange === "peak") {
      filteredPoints = curve.points.filter(p => p.day_offset >= 0 && p.day_offset <= 2);
    } else if (store.dateRange === "recovery") {
      filteredPoints = curve.points.filter(p => p.day_offset >= 3);
    }
    return { ...curve, points: filteredPoints };
  });
}

function renderFilteredPredictionChart() {
  const curves = getFilteredPredictionCurves();
  renderPredictionTimelineChart("predictionChartContainer", curves, {
    selectedNeighbourhood: store.neighbourhood
  });
}

function populateNeighbourhoodDropdown(neighbourhoods) {
  const select = document.getElementById("globalNeighbourhoodSelector");
  const chartFilter = document.getElementById("chartNeighbourhoodFilter");
  if (!select || !neighbourhoods) return;

  const optionsHtml = `<option value="all" selected>All ${neighbourhoods.length} Neighbourhoods</option>` +
    neighbourhoods.map(n => `<option value="${n.name}">${n.name} (${n.type})</option>`).join("");

  select.innerHTML = optionsHtml;
  if (chartFilter) {
    chartFilter.innerHTML = `<option value="all">All Neighbourhoods (Combined)</option>` +
      neighbourhoods.map(n => `<option value="${n.name}">${n.name} Only</option>`).join("");
  }
}

function populateDateDropdown(milestones) {
  const dateSelector = document.getElementById("globalDateSelector");
  if (!dateSelector || !milestones || milestones.length === 0) return;

  const currentVal = store.dayOffset.toString();
  dateSelector.innerHTML = milestones.map(m => {
    const isSelected = m.day_offset === store.dayOffset ? "selected" : "";
    const shortDate = m.date ? new Date(m.date).toLocaleDateString("en-GB", { day: "2-digit", month: "short", timeZone: "Asia/Kolkata" }) : m.date;
    const label = m.day_offset === 0 ? `${shortDate} (Diwali Night Peak)` : `${shortDate} (${m.phase_name})`;
    return `<option value="${m.day_offset}" ${isSelected}>${label}</option>`;
  }).join("");
}

// =============================================================================
// METRICS & TIMELINE SYNCHRONIZATION
// =============================================================================

function updateDashboardMetricsForOffset(offset) {
  if (!store.timelineMilestones || store.timelineMilestones.length === 0) return;

  const milestone = store.timelineMilestones.find(t => t.day_offset === offset) || store.timelineMilestones[0];
  const phaseLabelEl = document.getElementById("currentTimelinePhaseText");

  if (phaseLabelEl && milestone) {
    phaseLabelEl.textContent = `${milestone.date} – ${milestone.phase_name}`;
    phaseLabelEl.style.color = milestone.color;
  }

  // Update Summary Metric Cards
  const aqiVal = document.getElementById("currentAqiValue");
  const aqiBadge = document.getElementById("currentAqiBadge");
  const pm25Val = document.getElementById("currentPm25Value");
  const windVal = document.getElementById("currentWindValue");
  const tempVal = document.getElementById("currentTempValue");
  const peakVal = document.getElementById("peakAqiValue");

  if (aqiVal && milestone) {
    aqiVal.textContent = Math.round(milestone.city_avg_aqi);
    aqiVal.style.color = milestone.color;
  }

  if (aqiBadge && milestone) {
    aqiBadge.textContent = milestone.category;
    aqiBadge.style.color = milestone.color;
    aqiBadge.style.background = `${milestone.color}20`;
  }

  if (pm25Val && milestone) {
    const estPm25 = Math.round(milestone.city_avg_aqi * 0.48);
    pm25Val.textContent = estPm25;

    const pm25Badge = document.getElementById("pm25StandardBadge");
    if (pm25Badge) {
      const ratio = (estPm25 / 60.0).toFixed(1);
      pm25Badge.textContent = `${ratio}x NAAQS Standard`;
    }
  }

  if (windVal && milestone) {
    windVal.textContent = milestone.wind_speed;
  }

  if (tempVal && milestone) {
    tempVal.textContent = milestone.temperature || (store.weather ? store.weather.temperature_c : 22.0);
  }

  const weatherBadge = document.getElementById("weatherStatusBadge");
  if (weatherBadge && milestone) {
    weatherBadge.textContent = milestone.wind_speed <= 2.5 ? "Stagnant Inversion" : "Moderate Dispersion";
  }

  // Find city peak AQI across neighbourhoods
  if (peakVal && store.simulationData && store.simulationData.neighbourhoods) {
    const maxPeak = Math.max(...store.simulationData.neighbourhoods.map(n => n.predicted_peak_aqi));
    peakVal.textContent = maxPeak;

    const peakBadge = document.getElementById("peakAqiBadge");
    if (peakBadge) {
      const peakCat = getAQICategory(maxPeak);
      const peakColor = getAQIColor(maxPeak);
      peakBadge.textContent = peakCat;
      peakBadge.style.color = peakColor;
      peakBadge.style.background = `${peakColor}20`;
    }
  }
}

// =============================================================================
// TIMELINE PLAYBACK CONTROLLER
// =============================================================================

function setupTimelinePlayback() {
  const slider = document.getElementById("heatmapTimelineSlider");
  const playBtn = document.getElementById("timelinePlayBtn");

  if (slider) {
    slider.addEventListener("input", (e) => {
      const offset = parseInt(e.target.value, 10);
      syncTimelineOffset(offset);
    });
  }

  if (playBtn) {
    playBtn.addEventListener("click", () => {
      if (isPlaying) {
        pausePlayback();
      } else {
        startPlayback();
      }
    });
  }
}

function syncTimelineOffset(offset) {
  store.dayOffset = offset;
  const slider = document.getElementById("heatmapTimelineSlider");
  const dateSelector = document.getElementById("globalDateSelector");

  if (slider && parseInt(slider.value, 10) !== offset) {
    slider.value = offset;
  }
  if (dateSelector && parseInt(dateSelector.value, 10) !== offset) {
    dateSelector.value = offset.toString();
  }

  updateDashboardMetricsForOffset(offset);
  renderHeatmapMarkers(offset);
}

function startPlayback() {
  isPlaying = true;
  const playBtn = document.getElementById("timelinePlayBtn");
  if (playBtn) {
    playBtn.innerHTML = `<i data-lucide="pause" style="width: 18px; height: 18px;"></i>`;
    refreshIcons();
  }

  playbackTimer = setInterval(() => {
    let nextOffset = store.dayOffset + 1;
    if (nextOffset > 10) {
      nextOffset = -10;
    }
    syncTimelineOffset(nextOffset);
  }, 1500);
}

function pausePlayback() {
  isPlaying = false;
  if (playbackTimer) {
    clearInterval(playbackTimer);
    playbackTimer = null;
  }
  const playBtn = document.getElementById("timelinePlayBtn");
  if (playBtn) {
    playBtn.innerHTML = `<i data-lucide="play" style="width: 18px; height: 18px;"></i>`;
    refreshIcons();
  }
}

// =============================================================================
// COMPONENT RENDERING
// =============================================================================

function renderNeighbourhoodCards(neighbourhoods) {
  const container = document.getElementById("neighbourhoodCardsContainer");
  const countPill = document.getElementById("nhCountPill");
  if (!container || !neighbourhoods) return;

  let displayList = neighbourhoods;
  if (store.aqiFilter !== "all") {
    displayList = neighbourhoods.filter(nh => {
      const a = nh.current_aqi;
      if (store.aqiFilter === "good") return a <= 100;
      if (store.aqiFilter === "moderate") return a > 100 && a <= 200;
      if (store.aqiFilter === "poor") return a > 200 && a <= 400;
      if (store.aqiFilter === "severe") return a > 400;
      return true;
    });
  }

  if (countPill) {
    countPill.textContent = `${displayList.length} of ${neighbourhoods.length} Zones Shown`;
  }

  container.innerHTML = "";

  if (displayList.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 2.5rem; text-align: center; color: var(--text-secondary); background: var(--bg-card); border: 1px dashed var(--border-color); border-radius: 12px;">
        <i data-lucide="info" style="width: 28px; height: 28px; margin-bottom: 0.5rem; color: var(--primary-accent);"></i>
        <div style="font-weight: 600; font-size: 0.95rem; color: var(--text-main);">No Zones in Current AQI Band</div>
        <p style="font-size: 0.8rem; margin-top: 0.25rem;">Select "All AQI Levels" from the top filter toolbar to view all neighbourhoods.</p>
      </div>
    `;
    refreshIcons();
    return;
  }

  displayList.forEach(nh => {
    const color = getAQIColor(nh.current_aqi);
    const peakColor = getAQIColor(nh.predicted_peak_aqi);

    const card = document.createElement("div");
    card.className = "nh-card";
    card.innerHTML = `
      <div class="nh-card-header">
        <div>
          <div class="nh-name">${nh.name}</div>
          <span class="nh-zone-tag">${nh.type}</span>
        </div>
        <span class="status-badge" style="background: ${color}20; color: ${color};">
          ${getAQICategory(nh.current_aqi)}
        </span>
      </div>

      <div class="nh-stats-row">
        <div>
          <div style="font-size: 0.75rem; color: var(--text-secondary);">Current AQI</div>
          <div class="nh-aqi-stat" style="color: ${color};">${nh.current_aqi}</div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 0.75rem; color: var(--text-secondary);">Predicted Peak</div>
          <div style="font-size: 1.25rem; font-weight: 700; color: ${peakColor};">${nh.predicted_peak_aqi}</div>
        </div>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border-subtle); font-size: 0.75rem;">
        <span style="color: var(--text-secondary);">Modifier: ${nh.modifier > 1 ? `+${Math.round((nh.modifier - 1) * 100)}%` : (nh.modifier < 1 ? `-${Math.round((1 - nh.modifier) * 100)}%` : 'Baseline')}</span>
        <button class="btn btn-secondary nh-view-btn" data-nh="${nh.name}" style="padding: 0.25rem 0.65rem; font-size: 0.75rem;">
          Focus Map
        </button>
      </div>
    `;

    container.appendChild(card);
  });

  // Attach button click events
  container.querySelectorAll(".nh-view-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const nhName = btn.getAttribute("data-nh");
      focusNeighbourhoodOnMap(nhName);
      const chartFilter = document.getElementById("chartNeighbourhoodFilter");
      if (chartFilter) {
        chartFilter.value = nhName;
        renderPredictionTimelineChart("predictionChartContainer", store.predictionCurves, {
          selectedNeighbourhood: nhName
        });
      }
    });
  });
}

function renderAlertsList(alerts) {
  const container = document.getElementById("actionableAlertsList");
  const fullRegistry = document.getElementById("fullAlertsRegistry");
  if (!container || !alerts) return;

  const renderItems = (targetEl, list) => {
    if (list.length === 0) {
      targetEl.innerHTML = `<p style="color: var(--text-secondary); font-size: 0.85rem; padding: 1rem;">No advisories active for the selected location.</p>`;
      return;
    }

    targetEl.innerHTML = list.map(a => {
      const sevClass = a.severity.toLowerCase();
      const iconName = a.severity === "CRITICAL" ? "alert-triangle" : (a.severity === "WARNING" ? "alert-circle" : "info");

      return `
        <div class="alert-item severity-${sevClass}">
          <div class="alert-icon-wrap">
            <i data-lucide="${iconName}" style="width: 18px; height: 18px;"></i>
          </div>
          <div class="alert-body">
            <h4>${a.title}</h4>
            <p>${a.message || a.explanation}</p>
            <div class="alert-meta">
              <span><strong>Zone:</strong> ${a.neighbourhood} (${a.city})</span>
              <span><strong>Action:</strong> ${a.action_advised || a.precaution}</span>
              <span><strong>Trigger:</strong> ${a.trigger || 'Pollutant Threshold'}</span>
            </div>
          </div>
        </div>
      `;
    }).join("");
  };

  renderItems(container, alerts.slice(0, 4));
  if (fullRegistry) renderItems(fullRegistry, alerts);

  // Setup alert filter chips
  const filterChips = document.querySelectorAll("#alertFilterChips button");
  filterChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const sev = chip.getAttribute("data-severity");
      const filtered = sev ? alerts.filter(a => a.severity.toUpperCase() === sev.toUpperCase()) : alerts;
      renderItems(container, filtered);
      refreshIcons();
    });
  });

  refreshIcons();
}

function renderGovernanceTables(govData) {
  const sourcesBody = document.getElementById("governanceTableBody");
  const auditBody = document.getElementById("ingestionAuditTableBody");

  const sources = govData?.data_sources || govData?.sources || [];
  const auditLogs = govData?.audit_logs_recent || govData?.audit_logs || [];

  if (sourcesBody && sources.length > 0) {
    sourcesBody.innerHTML = sources.map(s => `
      <tr>
        <td><strong>${s.department}</strong></td>
        <td>${s.dataset_name}</td>
        <td><code>${s.integration_type}</code></td>
        <td><span class="status-pill"><span class="status-pulse"></span> ${s.status}</span></td>
        <td><strong>${(s.records_count || 0).toLocaleString()}</strong></td>
        <td><a href="${s.official_website || '#'}" target="_blank" rel="noopener noreferrer" style="color: var(--primary-accent); text-decoration: none; font-weight: 500;">Verify &nearr;</a></td>
      </tr>
    `).join("");
  }

  if (auditBody && auditLogs.length > 0) {
    auditBody.innerHTML = auditLogs.map(log => `
      <tr>
        <td>${new Date(log.timestamp).toLocaleString()}</td>
        <td><code>${log.connector_name || log.connector}</code></td>
        <td><span class="badge-provenance">${log.status}</span></td>
        <td><strong>${log.records_ingested}</strong></td>
        <td>${log.execution_time_seconds ? `${log.execution_time_seconds}s` : "Instant"}</td>
      </tr>
    `).join("");
  }
}

function renderTimelineTab(timeline) {
  const container = document.getElementById("timelineDetailedContainer");
  if (!container || !timeline) return;

  container.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 1rem;">
      ${timeline.map(t => `
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 1.1rem; border: 1px solid var(--border-color); border-radius: 12px; background: var(--bg-card);">
          <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 44px; height: 44px; border-radius: 50%; background: ${t.color}20; color: ${t.color}; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem;">
              ${t.day_offset === 0 ? 'T0' : (t.day_offset > 0 ? `+${t.day_offset}` : t.day_offset)}
            </div>
            <div>
              <div style="font-weight: 700; color: var(--text-main);">${t.phase_name}</div>
              <div style="font-size: 0.8rem; color: var(--text-secondary);">Date: ${t.date} &bull; Wind: ${t.wind_speed} km/h &bull; Humidity: ${t.humidity}% &bull; Temp: ${t.temperature || 22.0} °C</div>
            </div>
          </div>
          <div style="text-align: right;">
            <span class="status-badge" style="background: ${t.color}20; color: ${t.color}; font-size: 0.85rem;">
              AQI ${t.city_avg_aqi} (${t.category})
            </span>
          </div>
        </div>
      `).join("")}
    </div>
  `;
}

function renderEnvironmentTab(simData, weatherObj) {
  const container = document.getElementById("envFactorsContainer");
  if (!container) return;

  const windSpeed = weatherObj?.wind_speed_kmh || (simData ? simData.neighbourhoods[0]?.records[0]?.wind_speed : 2.8);
  const humidity = weatherObj?.humidity_pct || (simData ? simData.neighbourhoods[0]?.records[0]?.humidity : 68.0);
  const temp = weatherObj?.temperature_c || (simData ? simData.neighbourhoods[0]?.records[0]?.temperature : 22.0);

  container.innerHTML = `
    <div class="card">
      <div class="card-header">
        <h4 class="card-title"><i data-lucide="wind"></i> IMD Wind Velocity</h4>
      </div>
      <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
        Nocturnal surface winds &le; 2.5 km/h induce thermal stagnation, restricting multi-pollutant horizontal ventilation.
      </p>
      <div style="font-size: 1.75rem; font-weight: 800; color: var(--primary-accent);">${windSpeed} km/h</div>
    </div>

    <div class="card">
      <div class="card-header">
        <h4 class="card-title"><i data-lucide="droplet"></i> Relative Humidity & Mist</h4>
      </div>
      <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
        Autumn boundary cooling accelerates secondary aerosol condensation and formation of photochemical haze.
      </p>
      <div style="font-size: 1.75rem; font-weight: 800; color: #F59E0B;">${humidity}%</div>
    </div>

    <div class="card">
      <div class="card-header">
        <h4 class="card-title"><i data-lucide="thermometer"></i> Ambient Surface Temperature</h4>
      </div>
      <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
        Cooling ground layers inhibit vertical convection, trapping particulate emissions near the breathing zone.
      </p>
      <div style="font-size: 1.75rem; font-weight: 800; color: #10B981;">${temp} °C</div>
    </div>
  `;
}

// =============================================================================
// NAVIGATION & CONTROLS SETUP
// =============================================================================

function setupNavigationTabs() {
  const navItems = document.querySelectorAll(".nav-item");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const pageTitle = document.getElementById("pageTitleText");

  const titles = {
    dashboard: "Dashboard",
    heatmap: "Dedicated Geospatial Pollution Visualizer",
    predictions: "AI Scenario & Emission Predictor",
    timeline: "21-Day Phased Festival Timeline (T-10 to T+10)",
    environment: "IMD Weather & MoRTH Transport Factors",
    alerts: "Actionable Public Health Advisories",
    governance: "Official GoI Data Sources & Audit Log",
    settings: "System Configuration & Settings"
  };

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const targetTab = item.getAttribute("data-tab");
      navItems.forEach(n => n.classList.remove("active"));
      item.classList.add("active");

      tabPanes.forEach(pane => {
        pane.classList.remove("active");
        if (pane.id === `tab-${targetTab}`) {
          pane.classList.add("active");
        }
      });

      if (pageTitle && titles[targetTab]) {
        pageTitle.textContent = titles[targetTab];
      }

      // Map view synchronization on tab visibility
      if (targetTab === "heatmap") {
        setTimeout(initDedicatedHeatmap, 100);
      }
      if (targetTab === "dashboard") {
        setTimeout(initInteractiveMap, 100);
      }

      refreshIcons();
    });
  });
}

function setupTopBarControls() {
  const citySelector = document.getElementById("globalCitySelector");
  const nhSelector = document.getElementById("globalNeighbourhoodSelector");
  const dateSelector = document.getElementById("globalDateSelector");
  const dateRangeSelector = document.getElementById("globalDateRangeSelector");
  const aqiFilter = document.getElementById("globalAqiFilter");
  const dataSourceFilter = document.getElementById("globalDataSourceFilter");
  const chartFilter = document.getElementById("chartNeighbourhoodFilter");
  const refreshBtn = document.getElementById("refreshDashboardBtn");

  // 1. City Selector (Task 2 & 3: All 20 Cities Supported)
  if (citySelector) {
    citySelector.addEventListener("change", async (e) => {
      const selectedCity = e.target.value;
      store.city = selectedCity;
      store.neighbourhood = "all";
      await loadCityData(selectedCity);
    });
  }

  // 2. Neighbourhood Selector
  if (nhSelector) {
    nhSelector.addEventListener("change", (e) => {
      const selected = e.target.value;
      store.setNeighbourhood(selected);
      if (chartFilter) {
        chartFilter.value = selected;
        renderFilteredPredictionChart();
      }
      focusNeighbourhoodOnMap(selected);
    });
  }

  // 3. Date / Timeline Selector
  if (dateSelector) {
    dateSelector.addEventListener("change", (e) => {
      const offset = parseInt(e.target.value, 10);
      syncTimelineOffset(offset);
    });
  }

  // 4. Date Range Selector
  if (dateRangeSelector) {
    dateRangeSelector.addEventListener("change", (e) => {
      store.setDateRange(e.target.value);
      renderFilteredPredictionChart();
    });
  }

  // 5. AQI Severity Filter
  if (aqiFilter) {
    aqiFilter.addEventListener("change", (e) => {
      store.setAqiFilter(e.target.value);
      if (store.simulationData) {
        renderNeighbourhoodCards(store.simulationData.neighbourhoods);
        renderHeatmapMarkers(store.dayOffset);
      }
    });
  }

  // 6. Data Source Filter
  if (dataSourceFilter) {
    dataSourceFilter.addEventListener("change", (e) => {
      store.setDataSourceFilter(e.target.value);
      const provenanceBadge = document.querySelector(".header-actions .badge-provenance");
      if (provenanceBadge) {
        provenanceBadge.innerHTML = `<i data-lucide="shield-check" style="width: 14px; height: 14px;"></i> Source: ${e.target.value}`;
        refreshIcons();
      }
    });
  }

  // Chart Neighbourhood Filter
  if (chartFilter) {
    chartFilter.addEventListener("change", (e) => {
      const val = e.target.value;
      store.setNeighbourhood(val);
      renderFilteredPredictionChart();
      if (nhSelector) nhSelector.value = val;
      focusNeighbourhoodOnMap(val);
    });
  }

  // Refresh Button
  if (refreshBtn) {
    refreshBtn.addEventListener("click", async () => {
      refreshBtn.disabled = true;
      refreshBtn.innerHTML = `<i data-lucide="loader-2" class="lucide-spin" style="width: 16px; height: 16px;"></i> Refreshing...`;
      refreshIcons();
      await loadCityData(store.city);
      refreshBtn.disabled = false;
      refreshBtn.innerHTML = `<i data-lucide="refresh-cw" style="width: 16px; height: 16px;"></i> Refresh Data`;
      refreshIcons();
    });
  }
}

// =============================================================================
// TASK 5: SETTINGS TAB (THEME, DEFAULT CITY, THRESHOLD & PERSISTENCE)
// =============================================================================

function setupSettingsTab() {
  const form = document.getElementById("settingsForm");
  const radioLight = document.getElementById("themeRadioLight");
  const radioDark = document.getElementById("themeRadioDark");
  const defaultCity = document.getElementById("settingsDefaultCity");
  const intervalSelect = document.getElementById("settingsRefreshInterval");
  const thresholdSlider = document.getElementById("settingsAlertThreshold");
  const thresholdVal = document.getElementById("settingsThresholdValue");
  const resetBtn = document.getElementById("resetDefaultsBtn");
  const clearCacheBtn = document.getElementById("clearCacheBtn");

  if (radioLight && radioDark) {
    if (store.theme === "dark") {
      radioDark.checked = true;
    } else {
      radioLight.checked = true;
    }

    radioLight.addEventListener("change", () => {
      store.setTheme("light");
      updateThemeIcon("light");
      updateGoogleMapsTheme("light");
      renderHeatmapMarkers(store.dayOffset);
      renderFilteredPredictionChart();
      refreshIcons();
    });
    radioDark.addEventListener("change", () => {
      store.setTheme("dark");
      updateThemeIcon("dark");
      updateGoogleMapsTheme("dark");
      renderHeatmapMarkers(store.dayOffset);
      renderFilteredPredictionChart();
      refreshIcons();
    });
  }

  if (defaultCity) {
    const savedDefault = localStorage.getItem("aetherqi_default_city") || store.city || "Delhi";
    defaultCity.value = savedDefault;
  }

  if (thresholdSlider && thresholdVal) {
    const saved = localStorage.getItem("aetherqi_alert_threshold") || "400";
    thresholdSlider.value = saved;
    thresholdVal.textContent = `${saved} IND-AQI`;

    thresholdSlider.addEventListener("input", (e) => {
      thresholdVal.textContent = `${e.target.value} IND-AQI`;
    });
  }

  if (intervalSelect) {
    const savedInterval = localStorage.getItem("aetherqi_refresh_interval") || "60";
    intervalSelect.value = savedInterval;
  }

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const city = defaultCity ? defaultCity.value : "Delhi";
      const threshold = thresholdSlider ? thresholdSlider.value : "400";
      const interval = intervalSelect ? intervalSelect.value : "60";

      localStorage.setItem("aetherqi_default_city", city);
      localStorage.setItem("aetherqi_alert_threshold", threshold);
      localStorage.setItem("aetherqi_refresh_interval", interval);

      alert(`AetherQI Preferences Saved Successfully:\n• Default Startup City: ${city}\n• Severe Alert Threshold: ${threshold} IND-AQI\n• Sync Cadence: ${interval} minutes`);
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      localStorage.removeItem("aetherqi_default_city");
      localStorage.removeItem("aetherqi_alert_threshold");
      localStorage.removeItem("aetherqi_refresh_interval");
      if (defaultCity) defaultCity.value = "Delhi";
      if (thresholdSlider) {
        thresholdSlider.value = "400";
        thresholdVal.textContent = "400 IND-AQI";
      }
      alert("Settings reset to defaults.");
    });
  }

  if (clearCacheBtn) {
    clearCacheBtn.addEventListener("click", () => {
      if (confirm("Reset local cache and reload dashboard?")) {
        localStorage.clear();
        window.location.reload();
      }
    });
  }
}

function setupModals() {
  const overlay = document.getElementById("csvModalOverlay");
  const openBtn = document.getElementById("openCsvModalBtn");
  const closeBtn = document.getElementById("closeCsvModalBtn");
  const cancelBtn = document.getElementById("cancelCsvBtn");
  const form = document.getElementById("csvUploadForm");

  const open = () => { if (overlay) overlay.style.display = "flex"; };
  const close = () => { if (overlay) overlay.style.display = "none"; };

  if (openBtn) openBtn.addEventListener("click", open);
  if (closeBtn) closeBtn.addEventListener("click", close);
  if (cancelBtn) cancelBtn.addEventListener("click", close);

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fileInput = document.getElementById("csvFileInput");
      const sourceType = document.getElementById("csvSourceType").value;

      if (!fileInput.files || fileInput.files.length === 0) {
        alert("Please select a valid CSV file.");
        return;
      }

      const file = fileInput.files[0];
      const reader = new FileReader();

      reader.onload = async (evt) => {
        try {
          const content = evt.target.result;
          const res = await uploadCustomCSV(content, sourceType);
          alert(`Successfully ingested ${res.ingested_records} records from official CSV (${res.source_type}).`);
          close();
          await loadCityData(store.city);
        } catch (err) {
          alert(`CSV Ingestion Error: ${err.message}`);
        }
      };

      reader.readAsText(file);
    });
  }
}

function setupSimulationForm() {
  const form = document.getElementById("aiSimulationForm");
  const locSelect = document.getElementById("aiSimLocation");
  if (!form || !locSelect) return;

  fetchNeighbourhoods("Delhi").then(nhList => {
    locSelect.innerHTML = nhList.map(n => `
      <option value="${n.name}">${n.name} (${n.city || 'Delhi'})</option>
    `).join("");
  }).catch(() => {
    locSelect.innerHTML = `
      <option value="Anand Vihar, Delhi">Anand Vihar, Delhi</option>
      <option value="Connaught Place, Central Delhi">Connaught Place, Central Delhi</option>
      <option value="Rohini, Delhi">Rohini, Delhi</option>
      <option value="Dwarka, Delhi">Dwarka, Delhi</option>
      <option value="Okhla, Delhi">Okhla, Delhi</option>
    `;
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const location = locSelect.value;
    const hours = parseInt(document.getElementById("aiSimHours").value, 10);
    const scenario = document.getElementById("aiSimScenario").value;
    const resultsContainer = document.getElementById("aiForecastResults");

    resultsContainer.innerHTML = `
      <div style="padding: 2rem; text-align: center; color: var(--primary-accent);">
        <i data-lucide="loader-2" class="lucide-spin" style="width: 32px; height: 32px; margin-bottom: 0.5rem;"></i>
        <p>Executing Random Forest inference & CPCB multi-pollutant calculations...</p>
      </div>
    `;
    refreshIcons();

    try {
      const res = await predictAirQuality(location, scenario, hours);
      const isDark = store.theme === "dark";

      resultsContainer.innerHTML = `
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
              <h3 style="font-size: 1.05rem; font-weight: 700; color: var(--text-main);">${res.target_location}</h3>
              <p style="font-size: 0.8rem; color: var(--text-secondary);">Station: ${res.nearest_station_id} (${res.distance_km} km away, ${res.coverage_reliability} reliability)</p>
            </div>
            <span class="badge-provenance">Model Forecast</span>
          </div>

          <div id="aiForecastChartSvg" style="margin-bottom: 1rem;"></div>

          <div style="overflow-x: auto; max-height: 220px; overflow-y: auto;">
            <table class="data-sources-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>PM2.5 (µg/m³)</th>
                  <th>95% CI Range</th>
                  <th>Predicted AQI</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                ${res.predictions.map(p => `
                  <tr>
                    <td>${new Date(p.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                    <td><strong>${p.predicted_pm25}</strong></td>
                    <td style="color: var(--text-secondary);">${p.confidence_interval_low} – ${p.confidence_interval_high}</td>
                    <td><strong style="color: ${getAQIColor(p.predicted_cpcb_aqi)};">${p.predicted_cpcb_aqi}</strong></td>
                    <td><span class="status-badge" style="background: ${getAQIColor(p.predicted_cpcb_aqi)}20; color: ${getAQIColor(p.predicted_cpcb_aqi)};">${p.predicted_cpcb_category}</span></td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </div>
      `;

      renderForecastChart("aiForecastChartSvg", res.predictions);
      refreshIcons();
    } catch (err) {
      resultsContainer.innerHTML = `
        <div style="padding: 1.5rem; background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 12px; color: #EF4444;">
          <strong>Forecast Error:</strong> ${err.message}
        </div>
      `;
    }
  });
}
