"use strict";

const apiInput = document.getElementById("api-url");
const statusEl = document.getElementById("status");
const refreshBtn = document.getElementById("refresh");

let speedChart;
let pingChart;

function apiBase() {
  return apiInput.value.trim().replace(/\/$/, "");
}

function setStatus(msg, isError = false) {
  statusEl.textContent = msg;
  statusEl.classList.toggle("error", isError);
}

function fmt(value, digits = 1) {
  return value === null || value === undefined ? "—" : Number(value).toFixed(digits);
}

async function fetchJSON(path) {
  const resp = await fetch(apiBase() + path);
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status}`);
  }
  return resp.json();
}

function buildCharts() {
  const speedCtx = document.getElementById("speed-chart").getContext("2d");
  speedChart = new Chart(speedCtx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        { label: "Download (Mbps)", data: [], borderColor: "#38bdf8", tension: 0.3 },
        { label: "Upload (Mbps)", data: [], borderColor: "#a78bfa", tension: 0.3 },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#e2e8f0" } } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
      },
    },
  });

  const pingCtx = document.getElementById("ping-chart").getContext("2d");
  pingChart = new Chart(pingCtx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        { label: "Ping (ms)", data: [], borderColor: "#f472b6", tension: 0.3 },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#e2e8f0" } } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
      },
    },
  });
}

function renderCharts(measurements) {
  const labels = measurements.map((m) =>
    new Date(m.timestamp).toLocaleTimeString()
  );
  speedChart.data.labels = labels;
  speedChart.data.datasets[0].data = measurements.map((m) => m.download_mbps);
  speedChart.data.datasets[1].data = measurements.map((m) => m.upload_mbps);
  speedChart.update();

  pingChart.data.labels = labels;
  pingChart.data.datasets[0].data = measurements.map((m) => m.ping_ms);
  pingChart.update();
}

function renderStats(stats) {
  document.getElementById("sample-count").textContent = stats.count;
  const latest = stats.latest;
  document.getElementById("latest-download").textContent = fmt(
    latest && latest.download_mbps
  );
  document.getElementById("latest-upload").textContent = fmt(
    latest && latest.upload_mbps
  );
  document.getElementById("latest-ping").textContent = fmt(
    latest && latest.ping_ms
  );
}

async function refresh() {
  setStatus("Loading…");
  try {
    const [measurements, stats] = await Promise.all([
      fetchJSON("/measurements?limit=100"),
      fetchJSON("/stats"),
    ]);
    renderCharts(measurements);
    renderStats(stats);
    setStatus(`Updated ${new Date().toLocaleTimeString()}`);
  } catch (err) {
    setStatus(`Failed to load: ${err.message}`, true);
  }
}

refreshBtn.addEventListener("click", refresh);
buildCharts();
refresh();
setInterval(refresh, 15000);
