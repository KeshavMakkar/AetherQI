/**
 * AetherQI Visualization & Interactive Charting Engine
 * Supports High-DPI SVG rendering, dynamic light/dark theming, and tooltips.
 */

export function renderPredictionTimelineChart(containerId, seriesList, options = {}) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const isDark = document.documentElement.getAttribute("data-theme") === "dark";

  if (!seriesList || seriesList.length === 0) {
    container.innerHTML = `
      <div style="padding: 3rem; text-align: center; color: ${isDark ? '#A7B4C7' : '#64748B'};">
        <p>No prediction curve data available for selected location or filter.</p>
      </div>
    `;
    return;
  }

  const activeSeries = options.selectedNeighbourhood && options.selectedNeighbourhood.toLowerCase() !== "all"
    ? seriesList.filter(s => s.name.toLowerCase().includes(options.selectedNeighbourhood.toLowerCase()))
    : seriesList;

  const displayList = activeSeries.length > 0 ? activeSeries : seriesList;
  const primarySeries = displayList[0];

  const width = container.clientWidth || 800;
  const height = 340;
  const padding = { top: 35, right: 40, bottom: 50, left: 55 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  // Find max AQI across all displayed series
  let allAqis = [];
  displayList.forEach(s => {
    s.points.forEach(p => allAqis.push(p.aqi));
  });
  const maxVal = Math.max(Math.ceil((Math.max(...allAqis, 450) + 50) / 50) * 50, 500);
  const minVal = 0;

  const numPoints = primarySeries.points.length;
  const getX = (idx) => padding.left + (idx / Math.max(1, numPoints - 1)) * chartW;
  const getY = (val) => padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;

  // Theme Colors for SVG
  const gridColor = isDark ? "#333333" : "#E2E8F0";
  const axisTextColor = isDark ? "#D1D5DB" : "#4B5563";
  const subtextColor = isDark ? "#9CA3AF" : "#94A3B8";
  const markerBg = isDark ? "#382719" : "#EFF6FF";
  const markerBorder = isDark ? "#FF9F43" : "#60A5FA";
  const markerText = isDark ? "#FFB366" : "#2563EB";

  // Background Grid and Y-Ticks
  let gridSvg = "";
  const yTicks = 5;
  for (let i = 0; i <= yTicks; i++) {
    const val = Math.round(minVal + (i / yTicks) * (maxVal - minVal));
    const y = getY(val);
    gridSvg += `
      <line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="${gridColor}" stroke-width="1" stroke-dasharray="4,4" />
      <text x="${padding.left - 12}" y="${y + 4}" fill="${subtextColor}" font-size="11" font-family="Inter, -apple-system, sans-serif" text-anchor="end">${val}</text>
    `;
  }

  // Find Diwali Night Index (day_offset == 0)
  let diwaliIdx = primarySeries.points.findIndex(p => p.day_offset === 0);
  if (diwaliIdx === -1) diwaliIdx = Math.floor(numPoints / 2);
  const diwaliX = getX(diwaliIdx);

  // Vertical Diwali Night Marker (8 November 2026)
  const diwaliMarkerSvg = `
    <!-- Diwali Night Peak Marker -->
    <line x1="${diwaliX}" y1="${padding.top - 10}" x2="${diwaliX}" y2="${height - padding.bottom}" stroke="#EF4444" stroke-width="2" stroke-dasharray="5,5" />
    <rect x="${diwaliX - 58}" y="${padding.top - 24}" width="116" height="20" rx="4" fill="${markerBg}" stroke="${markerBorder}" stroke-width="1" />
    <text x="${diwaliX}" y="${padding.top - 10}" fill="${markerText}" font-size="10.5" font-weight="700" font-family="Inter, -apple-system, sans-serif" text-anchor="middle">
      Diwali (8 Nov Peak)
    </text>
  `;

  // X-Axis Labels across 21 Calendar Days (29 Oct -> 8 Nov -> 18 Nov)
  let xLabels = "";
  for (let i = 0; i < numPoints; i++) {
    const p = primarySeries.points[i];
    const x = getX(i);
    const isDiwali = (p.day_offset === 0);
    const isKeyTick = isDiwali || (p.day_offset % 2 === 0) || (i === 0) || (i === numPoints - 1);

    const dayLabel = isDiwali
      ? "8 Nov (Diwali)"
      : (p.day_offset > 0 ? `T+${p.day_offset}` : `T${p.day_offset}`);

    const labelColor = isDiwali ? "#EF4444" : axisTextColor;
    const labelWeight = isDiwali ? "800" : "500";
    const dateFormatted = p.date ? new Date(p.date).toLocaleDateString("en-GB", { day: "2-digit", month: "short", timeZone: "Asia/Kolkata" }) : "";

    xLabels += `
      <line x1="${x}" y1="${height - padding.bottom}" x2="${x}" y2="${height - padding.bottom + (isKeyTick ? 6 : 3)}" stroke="${isDark ? '#475569' : '#CBD5E1'}" />
      ${isKeyTick ? `
        <text x="${x}" y="${height - padding.bottom + 18}" fill="${labelColor}" font-size="${isDiwali ? '10' : '9.5'}" font-weight="${labelWeight}" font-family="Inter, -apple-system, sans-serif" text-anchor="middle">${dayLabel}</text>
        <text x="${x}" y="${height - padding.bottom + 31}" fill="${isDiwali ? '#EF4444' : subtextColor}" font-size="8.5" font-family="Inter, -apple-system, sans-serif" text-anchor="middle">${dateFormatted}</text>
      ` : ''}
    `;
  }

  // Series Line Colors (Light Blue for light mode, Light Orange for dark mode)
  const colors = isDark ? [
    { solid: "#FF9F43", light: "#FFB366" },
    { solid: "#10B981", light: "#34D399" },
    { solid: "#60A5FA", light: "#93C5FD" },
    { solid: "#A78BFA", light: "#C4B5FD" },
    { solid: "#F87171", light: "#FCA5A5" }
  ] : [
    { solid: "#2563EB", light: "#60A5FA" },
    { solid: "#059669", light: "#34D399" },
    { solid: "#D97706", light: "#FBBF24" },
    { solid: "#7C3AED", light: "#A78BFA" },
    { solid: "#DC2626", light: "#F87171" }
  ];

  let seriesSvg = "";
  let pointsSvg = "";

  displayList.forEach((series, sIdx) => {
    const colorObj = colors[sIdx % colors.length];
    const pts = series.points;

    let actualPath = "";
    let predPath = "";

    pts.forEach((p, i) => {
      const x = getX(i);
      const y = getY(p.aqi);

      if (p.day_offset <= 0) {
        actualPath += (actualPath === "" ? `M ${x} ${y}` : ` L ${x} ${y}`);
      }
      if (p.day_offset >= 0) {
        predPath += (predPath === "" ? `M ${x} ${y}` : ` L ${x} ${y}`);
      }

      const isActual = p.day_offset < 0;
      const pointColor = isActual ? colorObj.solid : colorObj.light;
      const strokeStyle = isDark ? "#181818" : "#FFFFFF";

      pointsSvg += `
        <circle cx="${x}" cy="${y}" r="4.5" fill="${pointColor}" stroke="${strokeStyle}" stroke-width="2" class="chart-point"
          data-series="${series.name}"
          data-date="${p.date}"
          data-offset="${p.day_offset}"
          data-aqi="${p.aqi}"
          data-pm25="${p.pm25}"
          data-temp="${p.temperature || 22.0}"
          data-actual="${isActual}"
          data-phase="${p.phase}"
          style="cursor: pointer; transition: transform 0.2s;">
        </circle>
      `;
    });

    seriesSvg += `
      <!-- Series: ${series.name} - Actual Baseline (Solid Line) -->
      <path d="${actualPath}" fill="none" stroke="${colorObj.solid}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
      <!-- Series: ${series.name} - Simulated Predictions (Dashed Line) -->
      <path d="${predPath}" fill="none" stroke="${colorObj.light}" stroke-width="3" stroke-dasharray="6,4" stroke-linecap="round" stroke-linejoin="round" />
    `;
  });

  container.innerHTML = `
    <div style="position: relative; width: 100%;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 1.25rem; font-size: 0.85rem; color: ${axisTextColor};">
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="display: inline-block; width: 22px; height: 3px; background: ${isDark ? '#FF9F43' : '#2563EB'}; border-radius: 2px;"></span>
            <span style="font-weight: 600;">Actual Baseline (T-10 to T-1: 29 Oct – 7 Nov)</span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="display: inline-block; width: 22px; height: 3px; border-top: 3px dashed ${isDark ? '#FFB366' : '#60A5FA'};"></span>
            <span style="font-weight: 600; color: ${isDark ? '#FFB366' : '#60A5FA'};">Simulated Prediction (T0 to T+10: 8 Nov – 18 Nov)</span>
          </div>
        </div>
        <div style="font-size: 0.75rem; background: ${markerBg}; color: ${markerText}; padding: 0.25rem 0.65rem; border-radius: 9999px; font-weight: 600; border: 1px solid ${markerBorder};">
          CPCB IND-AQI Scale (0–500)
        </div>
      </div>

      <svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" style="overflow: visible; background: transparent;">
        ${gridSvg}
        ${diwaliMarkerSvg}
        ${seriesSvg}
        ${pointsSvg}
        ${xLabels}
        <text transform="rotate(-90)" x="${-height / 2}" y="16" fill="${subtextColor}" font-size="11" font-family="Inter, -apple-system, sans-serif" text-anchor="middle">
          Air Quality Index (IND-AQI)
        </text>
      </svg>

      <!-- Hover Tooltip -->
      <div id="chartTooltip" style="position: absolute; display: none; background: ${isDark ? '#181818' : '#FFFFFF'}; border: 1px solid ${isDark ? '#333333' : '#E2E8F0'}; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4); border-radius: 8px; padding: 0.65rem 0.85rem; font-size: 0.8rem; pointer-events: none; z-index: 50; min-width: 180px; color: ${isDark ? '#FFFFFF' : '#111827'};">
      </div>
    </div>
  `;

  // Attach interactive tooltip events
  const tooltip = container.querySelector("#chartTooltip");
  const points = container.querySelectorAll(".chart-point");

  points.forEach(pt => {
    pt.addEventListener("mouseenter", () => {
      pt.setAttribute("r", "7");
      const name = pt.getAttribute("data-series");
      const aqi = pt.getAttribute("data-aqi");
      const pm25 = pt.getAttribute("data-pm25");
      const date = pt.getAttribute("data-date");
      const offset = pt.getAttribute("data-offset");
      const temp = pt.getAttribute("data-temp");
      const isActual = pt.getAttribute("data-actual") === "true";

      const badgeHtml = isActual
        ? `<span style="background: #ECFDF5; color: #047857; padding: 0.15rem 0.4rem; border-radius: 4px; font-weight: 600; font-size: 0.7rem;">Measured Baseline</span>`
        : `<span style="background: #EFF6FF; color: #1D4ED8; padding: 0.15rem 0.4rem; border-radius: 4px; font-weight: 600; font-size: 0.7rem;">Simulated Prediction</span>`;

      tooltip.innerHTML = `
        <div style="font-weight: 700; margin-bottom: 0.25rem;">${name}</div>
        <div style="color: ${subtextColor}; font-size: 0.75rem; margin-bottom: 0.4rem;">Date: ${date} (${offset >= 0 ? `T+${offset}` : `T${offset}`})</div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
          <span style="color: ${axisTextColor};">AQI:</span>
          <strong style="color: ${aqi > 400 ? '#EF4444' : (aqi > 300 ? '#F97316' : '#60A5FA')};">${aqi}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
          <span style="color: ${axisTextColor};">PM2.5:</span>
          <strong>${pm25} µg/m³</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem;">
          <span style="color: ${axisTextColor};">Temp:</span>
          <strong>${temp} °C</strong>
        </div>
        <div style="margin-top: 0.35rem;">${badgeHtml}</div>
      `;

      tooltip.style.display = "block";
      const rect = pt.getBoundingClientRect();
      const parentRect = container.getBoundingClientRect();
      tooltip.style.left = `${rect.left - parentRect.left + 10}px`;
      tooltip.style.top = `${rect.top - parentRect.top - 80}px`;
    });

    pt.addEventListener("mouseleave", () => {
      pt.setAttribute("r", "4.5");
      tooltip.style.display = "none";
    });
  });
}

export function renderForecastChart(containerId, predictions) {
  const container = document.getElementById(containerId);
  if (!container || !predictions || predictions.length === 0) return;

  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  const gridColor = isDark ? "#333333" : "#E2E8F0";
  const textColor = isDark ? "#D1D5DB" : "#64748B";
  const accentSolid = isDark ? "#FF9F43" : "#3B82F6";
  const accentLight = isDark ? "#FFB366" : "#60A5FA";
  const areaFill = isDark ? "rgba(255, 179, 102, 0.2)" : "rgba(96, 165, 250, 0.18)";
  const strokeBg = isDark ? "#181818" : "#FFFFFF";

  const width = container.clientWidth || 750;
  const height = 300;
  const padding = { top: 25, right: 35, bottom: 45, left: 55 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const maxVal = Math.max(...predictions.map(p => p.confidence_interval_high || p.predicted_pm25 * 1.3), 300);
  const minVal = 0;

  const getX = (idx) => padding.left + (idx / Math.max(1, predictions.length - 1)) * chartW;
  const getY = (val) => padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;

  // Build Confidence Interval Area Path
  let ciPath = "";
  for (let i = 0; i < predictions.length; i++) {
    const x = getX(i);
    const yHigh = getY(predictions[i].confidence_interval_high || predictions[i].predicted_pm25 * 1.15);
    ciPath += (i === 0 ? `M ${x} ${yHigh}` : ` L ${x} ${yHigh}`);
  }
  for (let i = predictions.length - 1; i >= 0; i--) {
    const x = getX(i);
    const yLow = getY(predictions[i].confidence_interval_low || predictions[i].predicted_pm25 * 0.85);
    ciPath += ` L ${x} ${yLow}`;
  }
  ciPath += " Z";

  // Build PM2.5 Line Path
  let pm25Line = "";
  for (let i = 0; i < predictions.length; i++) {
    const x = getX(i);
    const y = getY(predictions[i].predicted_pm25);
    pm25Line += (i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`);
  }

  // Grid Lines and Y-Axis Labels
  let gridSvg = "";
  const yTicks = 5;
  for (let i = 0; i <= yTicks; i++) {
    const val = Math.round(minVal + (i / yTicks) * (maxVal - minVal));
    const y = getY(val);
    gridSvg += `
      <line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="${gridColor}" stroke-dasharray="3,3" />
      <text x="${padding.left - 10}" y="${y + 4}" fill="${textColor}" font-size="11" text-anchor="end">${val}</text>
    `;
  }

  // X-Axis Time Labels
  let xLabels = "";
  const step = Math.max(1, Math.floor(predictions.length / 6));
  for (let i = 0; i < predictions.length; i += step) {
    const x = getX(i);
    const dt = new Date(predictions[i].timestamp);
    const label = `${dt.getHours()}:00`;
    xLabels += `
      <text x="${x}" y="${height - padding.bottom + 20}" fill="${textColor}" font-size="11" text-anchor="middle">${label}</text>
      <line x1="${x}" y1="${height - padding.bottom}" x2="${x}" y2="${height - padding.bottom + 6}" stroke="${gridColor}" />
    `;
  }

  // Circles for Data Points
  let points = "";
  for (let i = 0; i < predictions.length; i++) {
    const p = predictions[i];
    const x = getX(i);
    const y = getY(p.predicted_pm25);
    points += `
      <circle cx="${x}" cy="${y}" r="4" fill="${accentLight}" stroke="${strokeBg}" stroke-width="2">
        <title>Hour ${p.hour}:00 | PM2.5: ${p.predicted_pm25} µg/m³ | AQI: ${p.predicted_cpcb_aqi}</title>
      </circle>
    `;
  }

  container.innerHTML = `
    <svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" style="overflow: visible; background: transparent;">
      ${gridSvg}
      <path d="${ciPath}" fill="${areaFill}" />
      <path d="${pm25Line}" fill="none" stroke="${accentSolid}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
      ${points}
      ${xLabels}
      <text x="${width / 2}" y="${height - 5}" fill="${textColor}" font-size="11" text-anchor="middle">Forecast Horizon (Hourly Progression)</text>
      <text transform="rotate(-90)" x="${-height / 2}" y="15" fill="${textColor}" font-size="11" text-anchor="middle">PM2.5 (µg/m³)</text>
    </svg>
  `;
}

export function renderFeatureImportance(containerId, featureList) {
  const container = document.getElementById(containerId);
  if (!container || !featureList) return;

  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  const maxImp = Math.max(...featureList.map(f => f.importance), 0.01);
  const barColor = isDark ? "#FFB366" : "#60A5FA";
  const barTrack = isDark ? "#26201A" : "#F1F5F9";
  let bars = "";

  featureList.slice(0, 8).forEach(item => {
    const pct = Math.round((item.importance / maxImp) * 100);
    bars += `
      <div style="margin-bottom: 0.75rem;">
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 0.25rem;">
          <span style="font-weight: 600; color: ${isDark ? '#FFFFFF' : '#1E293B'};">${item.feature}</span>
          <span style="color: ${isDark ? '#D1D5DB' : '#64748B'};">${(item.importance * 100).toFixed(1)}%</span>
        </div>
        <div style="background: ${barTrack}; border-radius: 9999px; height: 8px; overflow: hidden;">
          <div style="background: ${barColor}; height: 100%; width: ${pct}%; border-radius: 9999px;"></div>
        </div>
      </div>
    `;
  });

  container.innerHTML = `
    <div style="background: ${isDark ? '#181818' : '#FFFFFF'}; border: 1px solid ${isDark ? '#333333' : '#E2E8F0'}; border-radius: 12px; padding: 1.25rem;">
      <h4 style="font-size: 0.95rem; font-weight: 700; color: ${isDark ? '#FFFFFF' : '#111827'}; margin-bottom: 1rem;">
        Random Forest Model Feature Weights
      </h4>
      ${bars}
    </div>
  `;
}
