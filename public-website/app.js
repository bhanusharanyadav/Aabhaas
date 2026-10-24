const API_BASE = (window.AABHAAS_CONFIG?.API_BASE_URL || "").replace(/\/$/, "");
const POLL_INTERVAL_MS = 5000;

const statusCard = document.getElementById("status-card");
const statusIcon = document.getElementById("status-icon");
const statusTitle = document.getElementById("status-title");
const statusMessage = document.getElementById("status-message");
const statusLocation = document.getElementById("status-location");
const statusUpdated = document.getElementById("status-updated");
const connectionState = document.getElementById("connection-state");
const modal = document.getElementById("alert-modal");
const modalPanel = document.getElementById("modal-panel");
const modalTitle = document.getElementById("modal-title");
const modalMessage = document.getElementById("modal-message");
const modalSeverity = document.getElementById("modal-severity");
const modalLocation = document.getElementById("modal-location");
const modalTime = document.getElementById("modal-time");
const dismissButton = document.getElementById("dismiss-modal");

let lastPopupAlertId = null;
let dismissedAlertIds = new Set();

function formatTime(value) {
  if (!value) return "Unknown";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

// ---------------------------------------------------------------------------
// Dam Warning Siren — Web Audio API
//
// Replicates a civil-defence / dam-break siren:
//   • Sawtooth oscillator for the raw, penetrating timbre
//   • Slow exponential frequency sweep: 300 Hz → 1100 Hz (3 s rise)
//     then back 1100 Hz → 300 Hz (3 s fall)  — one cycle = 6 s
//   • Second oscillator one octave lower adds body / rumble
//   • Loops seamlessly using Web Audio API parameter scheduling
// ---------------------------------------------------------------------------

let audioCtx = null;
let sirenOsc1 = null;   // main high-frequency oscillator
let sirenOsc2 = null;   // sub-octave rumble oscillator
let sirenGain = null;   // master volume node
let sirenActive = false;
let audioUnlocked = false;

// ── Configuration ──
const SIREN_AUDIO_SRC = "C:\Users\bhanu\OneDrive\Desktop\AI-Hybrid-Landslide Prediction\sound alert\mixkit-sci-fi-ship-siren-alert-1653.wav"; // Path to your file

const PITCH_LOW = 0.6;          // Normal speed / lower pitch factor
const PITCH_HIGH = 1.8;         // High speed / higher pitch factor
const RISE_TIME = 0.1;          // Seconds to ramp up
const FALL_TIME = 0.1;          // Seconds to ramp down
const CYCLE_DURATION = RISE_TIME + FALL_TIME;
const SIREN_VOLUME = 0.35;      // Master gain (0–1)

// ── State Variables ──
let audioCtx = null;
let audioBuffer = null;
let sirenSource = null;
let sirenGain = null;
let sirenActive = false;
let scheduleTimeout = null;

/** Lazily initialize and ensure AudioContext is active. */
async function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === "suspended") {
    await audioCtx.resume();
  }
  return audioCtx;
}

/** Preload and decode your audio file into memory. */
async function loadSirenBuffer() {
  if (audioBuffer) return audioBuffer;
  const ctx = await getAudioContext();
  const response = await fetch(SIREN_AUDIO_SRC);
  const arrayBuffer = await response.arrayBuffer();
  audioBuffer = await ctx.decodeAudioData(arrayBuffer);
  return audioBuffer;
}

/** Schedule one pitch sweep cycle on the audio file's playback rate. */
function scheduleWailCycle(sourceNode, t) {
  const peakTime = t + RISE_TIME;
  const endTime = t + CYCLE_DURATION;

  // Sweep playback speed: low -> high -> low
  sourceNode.playbackRate.exponentialRampToValueAtTime(PITCH_HIGH, peakTime);
  sourceNode.playbackRate.exponentialRampToValueAtTime(PITCH_LOW, endTime);

  return endTime;
}

/** Start the looping audio file with pitch modulation. */
async function startSiren() {
  if (sirenActive) return;
  sirenActive = true;

  try {
    const ctx = await getAudioContext();
    const buffer = await loadSirenBuffer();

    // ── Create Audio Source from your file ──
    sirenSource = ctx.createBufferSource();
    sirenSource.buffer = buffer;
    sirenSource.loop = true; // Loop audio continuously

    // ── Master Gain & Routing ──
    sirenGain = ctx.createGain();
    sirenGain.gain.value = 0; // Start muted, fade in

    sirenSource.connect(sirenGain);
    sirenGain.connect(ctx.destination);

    const now = ctx.currentTime;

    // Set initial pitch
    sirenSource.playbackRate.setValueAtTime(PITCH_LOW, now);

    // Fade in over 0.3s
    sirenGain.gain.setValueAtTime(0.0001, now);
    sirenGain.gain.linearRampToValueAtTime(SIREN_VOLUME, now + 0.3);

    // Start playback
    sirenSource.start(now);

    // Pre-schedule wail sweeps
    let nextCycleTime = now;
    const LOOK_AHEAD_CYCLES = 4;

    for (let i = 0; i < LOOK_AHEAD_CYCLES; i++) {
      nextCycleTime = scheduleWailCycle(sirenSource, nextCycleTime);
    }

    // Maintain future sweep schedule
    function maintainSchedule() {
      if (!sirenActive) return;
      const currentTime = ctx.currentTime;
      while (nextCycleTime < currentTime + CYCLE_DURATION * LOOK_AHEAD_CYCLES) {
        nextCycleTime = scheduleWailCycle(sirenSource, nextCycleTime);
      }
      scheduleTimeout = setTimeout(maintainSchedule, (CYCLE_DURATION * 1000) / 2);
    }

    scheduleTimeout = setTimeout(maintainSchedule, (CYCLE_DURATION * 1000) / 2);

  } catch (err) {
    console.warn("Siren audio file could not start:", err);
    sirenActive = false;
  }
}

/** Fade out and stop the audio file. */
function stopSiren() {
  if (!sirenActive) return;
  sirenActive = false;
  clearTimeout(scheduleTimeout);

  try {
    if (sirenGain && audioCtx) {
      const now = audioCtx.currentTime;
      sirenGain.gain.cancelScheduledValues(now);
      sirenGain.gain.setValueAtTime(sirenGain.gain.value, now);
      sirenGain.gain.linearRampToValueAtTime(0.0001, now + 0.5); // 0.5s fade out

      setTimeout(() => {
        try { sirenSource && sirenSource.stop(); } catch (_) { }
        try { sirenGain && sirenGain.disconnect(); } catch (_) { }
        sirenSource = sirenGain = null;
      }, 600);
    }
  } catch (err) {
    console.warn("Siren stop error:", err);
  }
}

// Unlock audio on the first user interaction
window.addEventListener("pointerdown", () => {
  if (audioCtx && audioCtx.state === "suspended") {
    audioCtx.resume();
  }
}, { passive: true });
// ---------------------------------------------------------------------------
// Modal
// ---------------------------------------------------------------------------

function showPopup(alert) {
  if (!alert || !alert.id || dismissedAlertIds.has(alert.id) || lastPopupAlertId === alert.id) return;
  lastPopupAlertId = alert.id;

  modalTitle.textContent = alert.title || `${alert.severity || "LANDSLIDE"} RISK ALERT`;
  modalMessage.textContent = alert.message || "A landslide risk alert has been issued.";
  modalSeverity.textContent = `Severity: ${alert.severity || "UNKNOWN"}`;
  modalLocation.textContent = `Location: ${alert.location || "Not specified"}`;
  modalTime.textContent = `Issued: ${formatTime(alert.created_at)}`;
  modalPanel.className = `modal-panel severity-${String(alert.severity || "high").toLowerCase()}`;

  modal.hidden = false;
  dismissButton.focus();

  // 🚨 Start dam warning siren immediately
  startSiren();
}

// Dismiss via button
dismissButton.addEventListener("click", () => {
  if (lastPopupAlertId) dismissedAlertIds.add(lastPopupAlertId);
  modal.hidden = true;
  stopSiren();
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
      statusCard.className = "status-card status-alert";
      statusIcon.textContent = "!";
      statusTitle.textContent = alert.title || `${alert.severity || "ACTIVE"} LANDSLIDE ALERT`;
      statusMessage.textContent = alert.message || "An alert is active for this monitored area.";
      statusLocation.textContent = `Location: ${alert.location || "Not specified"}`;
      statusUpdated.textContent = `Issued: ${formatTime(alert.created_at)}`;
      showPopup(alert);
    } else {
      statusCard.className = "status-card status-safe";
      statusIcon.textContent = "\u2713";
      statusTitle.textContent = "No active alert";
      statusMessage.textContent = "No active alert is currently available from the Aabhaas alert service. This does not guarantee that the area is safe.";
      statusLocation.textContent = "Location: monitored area";
      statusUpdated.textContent = `Checked: ${new Date().toLocaleTimeString()}`;
      lastPopupAlertId = null;
    }
  } catch (error) {
    connectionState.textContent = "Connection unavailable";
    statusCard.className = "status-card status-unknown";
    statusIcon.textContent = "!";
    statusTitle.textContent = "Alert status unavailable";
    statusMessage.textContent = "The alert service could not be reached. Do not interpret this as a safe status; check official local sources.";
    statusLocation.textContent = "Location: \u2014";
    statusUpdated.textContent = `Last attempt: ${new Date().toLocaleTimeString()}`;
    console.error("Aabhaas alert check failed:", error);
  }
}

refreshAlert();
setInterval(refreshAlert, POLL_INTERVAL_MS);
