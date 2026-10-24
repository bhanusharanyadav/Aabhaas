const API_BASE = (window.AABHAAS_CONFIG?.API_BASE_URL || "").replace(/\/$/, "");
const POLL_INTERVAL_MS = 5000;

const statusCard    = document.getElementById("status-card");
const statusIcon    = document.getElementById("status-icon");
const statusTitle   = document.getElementById("status-title");
const statusMessage = document.getElementById("status-message");
const statusLocation = document.getElementById("status-location");
const statusUpdated  = document.getElementById("status-updated");
const connectionState = document.getElementById("connection-state");
const modal         = document.getElementById("alert-modal");
const modalPanel    = document.getElementById("modal-panel");
const modalTitle    = document.getElementById("modal-title");
const modalMessage  = document.getElementById("modal-message");
const modalSeverity = document.getElementById("modal-severity");
const modalLocation = document.getElementById("modal-location");
const modalTime     = document.getElementById("modal-time");
const dismissButton = document.getElementById("dismiss-modal");

let lastPopupAlertId  = null;
let dismissedAlertIds = new Set();

function formatTime(value) {
  if (!value) return "Unknown";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

// ---------------------------------------------------------------------------
// Hazard Siren — Web Audio API (no audio file needed)
// ---------------------------------------------------------------------------

let audioCtx    = null;
let sirenNodes  = null;   // { osc, lfo, gain, lfoGain }
let sirenActive = false;
let audioUnlocked = false;

/** Lazily create / resume the AudioContext (browser autoplay policy). */
function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === "suspended") {
    audioCtx.resume().catch(() => {});
  }
  return audioCtx;
}

/**
 * Pick siren parameters based on alert severity.
 *   CRITICAL — fast, high-pitched wail   (900–1400 Hz, 2 Hz sweep)
 *   HIGH      — classic emergency siren   (700–1100 Hz, 1.2 Hz sweep)
 *   MODERATE  — slower warble             (500–800  Hz, 0.7 Hz sweep)
 *   LOW       — gentle alert tone         (400–600  Hz, 0.4 Hz sweep)
 */
function sirenParamsForSeverity(severity) {
  switch (String(severity || "").toUpperCase()) {
    case "CRITICAL": return { baseFreq: 900,  topFreq: 1400, sweepRate: 2.0, volume: 0.30 };
    case "HIGH":     return { baseFreq: 700,  topFreq: 1100, sweepRate: 1.2, volume: 0.22 };
    case "MODERATE": return { baseFreq: 500,  topFreq: 800,  sweepRate: 0.7, volume: 0.16 };
    default:         return { baseFreq: 400,  topFreq: 600,  sweepRate: 0.4, volume: 0.10 };
  }
}

/** Start the looping siren. Idempotent — safe to call multiple times. */
function startSiren(severity) {
  if (sirenActive) return;
  try {
    const ctx = getAudioContext();
    const { baseFreq, topFreq, sweepRate, volume } = sirenParamsForSeverity(severity);

    // Main oscillator — produces the raw siren tone
    const osc = ctx.createOscillator();
    osc.type = "sawtooth";
    osc.frequency.value = baseFreq;

    // LFO — sweeps the pitch up and down continuously
    const lfo = ctx.createOscillator();
    lfo.type = "sine";
    lfo.frequency.value = sweepRate;

    // LFO gain — sets how wide the frequency swing is
    const lfoGain = ctx.createGain();
    lfoGain.gain.value = (topFreq - baseFreq) / 2;

    // Master gain — overall volume
    const gain = ctx.createGain();
    gain.gain.value = volume;

    // Signal graph: LFO → lfoGain → osc.frequency  (FM modulation)
    lfo.connect(lfoGain);
    lfoGain.connect(osc.frequency);

    // Signal graph: osc → gain → speakers
    osc.connect(gain);
    gain.connect(ctx.destination);

    lfo.start();
    osc.start();

    sirenNodes  = { osc, lfo, gain, lfoGain };
    sirenActive = true;
  } catch (err) {
    console.warn("Aabhaas siren could not start:", err);
  }
}

/** Smoothly fade out and stop the siren (0.6 s ramp). */
function stopSiren() {
  if (!sirenActive || !sirenNodes) return;
  try {
    const { osc, lfo, gain } = sirenNodes;
    const ctx = getAudioContext();
    const now = ctx.currentTime;

    gain.gain.setValueAtTime(gain.gain.value, now);
    gain.gain.linearRampToValueAtTime(0, now + 0.6);

    setTimeout(() => {
      try { osc.stop(); } catch (_) {}
      try { lfo.stop(); } catch (_) {}
      osc.disconnect();
      lfo.disconnect();
      gain.disconnect();
    }, 700);
  } catch (err) {
    console.warn("Aabhaas siren stop error:", err);
  } finally {
    sirenNodes  = null;
    sirenActive = false;
  }
}

/**
 * Browsers block AudioContext until a user gesture.
 * We prime the context on the very first interaction so the siren
 * can fire immediately when a new alert is detected.
 */
function unlockAudioOnFirstInteraction() {
  if (audioUnlocked) return;
  const unlock = () => {
    if (audioUnlocked) return;
    audioUnlocked = true;
    getAudioContext();
    document.removeEventListener("click",      unlock);
    document.removeEventListener("keydown",    unlock);
    document.removeEventListener("touchstart", unlock);
  };
  document.addEventListener("click",      unlock, { once: true });
  document.addEventListener("keydown",    unlock, { once: true });
  document.addEventListener("touchstart", unlock, { once: true });
}

unlockAudioOnFirstInteraction();

// ---------------------------------------------------------------------------
// Modal
// ---------------------------------------------------------------------------

function showPopup(alert) {
  if (!alert || !alert.id || dismissedAlertIds.has(alert.id) || lastPopupAlertId === alert.id) return;
  lastPopupAlertId = alert.id;
  modalTitle.textContent   = alert.title   || `${alert.severity || "LANDSLIDE"} RISK ALERT`;
  modalMessage.textContent = alert.message || "A landslide risk alert has been issued.";
  modalSeverity.textContent = `Severity: ${alert.severity || "UNKNOWN"}`;
  modalLocation.textContent = `Location: ${alert.location || "Not specified"}`;
  modalTime.textContent     = `Issued: ${formatTime(alert.created_at)}`;
  modalPanel.className = `modal-panel severity-${String(alert.severity || "high").toLowerCase()}`;
  modal.hidden = false;
  dismissButton.focus();

  // 🔊 Play the hazard siren for this alert
  startSiren(alert.severity);
}

// Dismiss via button
dismissButton.addEventListener("click", () => {
  if (lastPopupAlertId) dismissedAlertIds.add(lastPopupAlertId);
  modal.hidden = true;
  stopSiren();  // 🔇 Fade out siren on dismiss
});

// Dismiss via Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !modal.hidden) {
    if (lastPopupAlertId) dismissedAlertIds.add(lastPopupAlertId);
    modal.hidden = true;
    stopSiren();
  }
});

// ---------------------------------------------------------------------------
// Polling
// ---------------------------------------------------------------------------

async function refreshAlert() {
  try {
    if (!API_BASE || API_BASE.includes("YOUR_API_URL")) throw new Error("API URL is not configured.");
    const response = await fetch(`${API_BASE}/api/alerts/active`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Alert API returned HTTP ${response.status}.`);
    const payload = await response.json();
    connectionState.textContent = "Connected \u00b7 checking every 5 seconds";
    const alert = payload.alert;

    if (alert && alert.status === "ACTIVE") {
      statusCard.className     = "status-card status-alert";
      statusIcon.textContent   = "!";
      statusTitle.textContent  = alert.title   || `${alert.severity || "ACTIVE"} LANDSLIDE ALERT`;
      statusMessage.textContent = alert.message || "An alert is active for this monitored area.";
      statusLocation.textContent = `Location: ${alert.location || "Not specified"}`;
      statusUpdated.textContent  = `Issued: ${formatTime(alert.created_at)}`;
      showPopup(alert);
    } else {
      statusCard.className     = "status-card status-safe";
      statusIcon.textContent   = "\u2713";
      statusTitle.textContent  = "No active alert";
      statusMessage.textContent = "No active alert is currently available from the Aabhaas alert service. This does not guarantee that the area is safe.";
      statusLocation.textContent = "Location: monitored area";
      statusUpdated.textContent  = `Checked: ${new Date().toLocaleTimeString()}`;
      lastPopupAlertId = null;
    }
  } catch (error) {
    connectionState.textContent  = "Connection unavailable";
    statusCard.className         = "status-card status-unknown";
    statusIcon.textContent       = "!";
    statusTitle.textContent      = "Alert status unavailable";
    statusMessage.textContent    = "The alert service could not be reached. Do not interpret this as a safe status; check official local sources.";
    statusLocation.textContent   = "Location: \u2014";
    statusUpdated.textContent    = `Last attempt: ${new Date().toLocaleTimeString()}`;
    console.error("Aabhaas alert check failed:", error);
  }
}

refreshAlert();
setInterval(refreshAlert, POLL_INTERVAL_MS);
