const API_BASE = (window.AABHAAS_CONFIG?.API_BASE_URL || "").replace(/\/$/, "");
const POLL_INTERVAL_MS = 5000;

const statusCard     = document.getElementById("status-card");
const statusIcon     = document.getElementById("status-icon");
const statusTitle    = document.getElementById("status-title");
const statusMessage  = document.getElementById("status-message");
const statusLocation = document.getElementById("status-location");
const statusUpdated  = document.getElementById("status-updated");
const connectionState = document.getElementById("connection-state");
const modal          = document.getElementById("alert-modal");
const modalPanel     = document.getElementById("modal-panel");
const modalTitle     = document.getElementById("modal-title");
const modalMessage   = document.getElementById("modal-message");
const modalSeverity  = document.getElementById("modal-severity");
const modalLocation  = document.getElementById("modal-location");
const modalTime      = document.getElementById("modal-time");
const dismissButton  = document.getElementById("dismiss-modal");

let lastPopupAlertId  = null;
let dismissedAlertIds = new Set();

function formatTime(value) {
  if (!value) return "Unknown";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

// ---------------------------------------------------------------------------
// SOS Alarm — Web Audio API scheduled Morse code (· · · — — — · · ·)
// ---------------------------------------------------------------------------

let audioCtx      = null;
let sosLoopTimer  = null;   // setTimeout handle for loop scheduling
let sosActive     = false;
let audioUnlocked = false;

/** Lazily create / resume the AudioContext. */
function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === "suspended") {
    audioCtx.resume();   // no .catch — intentional, fire-and-forget
  }
  return audioCtx;
}

/**
 * Schedule one complete SOS pattern starting at `startTime` (AudioContext time).
 *
 * Morse timing (unit = 0.12 s):
 *   dot      = 1 unit  (0.12 s)
 *   dash     = 3 units (0.36 s)
 *   intra-gap= 1 unit  (0.12 s) between elements of same letter
 *   inter-gap= 3 units (0.36 s) between letters
 *   word-gap = 7 units (0.84 s) between SOS repeats
 *
 * Pattern:  S=···  O=———  S=···
 * Returns the AudioContext time when this SOS cycle ends.
 */
function scheduleSOS(ctx, startTime, freq, volume) {
  const unit     = 0.12;
  const dot      = unit;
  const dash     = 3 * unit;
  const intraGap = unit;
  const interGap = 3 * unit;
  const wordGap  = 7 * unit;

  // Elements: true = dot, false = dash
  const pattern = [
    // S
    true, true, true,
    // O
    false, false, false,
    // S
    true, true, true,
  ];

  // Letter boundaries (after which element index a letter ends, 0-based)
  const letterBoundaries = new Set([2, 5]); // after S, after O (not after last S)

  let t = startTime;

  pattern.forEach((isDot, i) => {
    const duration = isDot ? dot : dash;

    // Create oscillator for this element
    const osc  = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = "sine";
    osc.frequency.value = freq;

    // Tiny attack/release (3 ms) to avoid clicks
    gain.gain.setValueAtTime(0, t);
    gain.gain.linearRampToValueAtTime(volume, t + 0.003);
    gain.gain.setValueAtTime(volume, t + duration - 0.003);
    gain.gain.linearRampToValueAtTime(0, t + duration);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(t);
    osc.stop(t + duration);

    t += duration;

    // Choose gap after this element
    if (i < pattern.length - 1) {
      t += letterBoundaries.has(i) ? interGap : intraGap;
    }
  });

  // Return the time when the next SOS repeat should start
  return t + wordGap;
}

/** Start the looping SOS alarm. Idempotent. */
function startSOS() {
  if (sosActive) return;
  sosActive = true;

  const ctx    = getAudioContext();
  const freq   = 880;   // A5 — piercing but not painful
  const volume = 0.4;

  function scheduleLoop() {
    if (!sosActive) return;
    // Schedule two SOS repetitions ahead for seamless looping
    const now      = ctx.currentTime;
    const nextTime = scheduleSOS(ctx, now, freq, volume);
    // Re-schedule ~200 ms before the current cycle ends
    const delay    = Math.max(0, (nextTime - now - 0.2) * 1000);
    sosLoopTimer   = setTimeout(scheduleLoop, delay);
  }

  scheduleLoop();
}

/** Stop the SOS alarm. */
function stopSOS() {
  sosActive = false;
  if (sosLoopTimer !== null) {
    clearTimeout(sosLoopTimer);
    sosLoopTimer = null;
  }
  // AudioContext stays alive; future tones already scheduled will complete
  // within <1 s then silence because sosActive is false.
}

/**
 * Browsers block AudioContext until a user gesture.
 * We prime it on the very first interaction so SOS plays the moment
 * an alert popup appears — no extra click needed.
 */
function unlockAudio() {
  if (audioUnlocked) return;
  audioUnlocked = true;
  getAudioContext();   // create + resume
}

// Unlock on first touch/click/key on the whole page
["click", "keydown", "touchstart", "pointerdown"].forEach((evt) => {
  document.addEventListener(evt, unlockAudio, { once: true, passive: true });
});

// ---------------------------------------------------------------------------
// Modal
// ---------------------------------------------------------------------------

function showPopup(alert) {
  if (!alert || !alert.id || dismissedAlertIds.has(alert.id) || lastPopupAlertId === alert.id) return;
  lastPopupAlertId = alert.id;

  modalTitle.textContent    = alert.title   || `${alert.severity || "LANDSLIDE"} RISK ALERT`;
  modalMessage.textContent  = alert.message || "A landslide risk alert has been issued.";
  modalSeverity.textContent = `Severity: ${alert.severity || "UNKNOWN"}`;
  modalLocation.textContent = `Location: ${alert.location  || "Not specified"}`;
  modalTime.textContent     = `Issued: ${formatTime(alert.created_at)}`;
  modalPanel.className = `modal-panel severity-${String(alert.severity || "high").toLowerCase()}`;

  modal.hidden = false;
  dismissButton.focus();

  // 🔊 Start SOS alarm immediately when popup is shown
  startSOS();
}

// Dismiss via button
dismissButton.addEventListener("click", () => {
  if (lastPopupAlertId) dismissedAlertIds.add(lastPopupAlertId);
  modal.hidden = true;
  stopSOS();   // 🔇 Stop SOS on dismiss
});

// Dismiss via Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !modal.hidden) {
    if (lastPopupAlertId) dismissedAlertIds.add(lastPopupAlertId);
    modal.hidden = true;
    stopSOS();
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
      statusCard.className      = "status-card status-alert";
      statusIcon.textContent    = "!";
      statusTitle.textContent   = alert.title   || `${alert.severity || "ACTIVE"} LANDSLIDE ALERT`;
      statusMessage.textContent = alert.message || "An alert is active for this monitored area.";
      statusLocation.textContent = `Location: ${alert.location || "Not specified"}`;
      statusUpdated.textContent  = `Issued: ${formatTime(alert.created_at)}`;
      showPopup(alert);
    } else {
      statusCard.className      = "status-card status-safe";
      statusIcon.textContent    = "\u2713";
      statusTitle.textContent   = "No active alert";
      statusMessage.textContent = "No active alert is currently available from the Aabhaas alert service. This does not guarantee that the area is safe.";
      statusLocation.textContent = "Location: monitored area";
      statusUpdated.textContent  = `Checked: ${new Date().toLocaleTimeString()}`;
      lastPopupAlertId = null;
    }
  } catch (error) {
    connectionState.textContent   = "Connection unavailable";
    statusCard.className          = "status-card status-unknown";
    statusIcon.textContent        = "!";
    statusTitle.textContent       = "Alert status unavailable";
    statusMessage.textContent     = "The alert service could not be reached. Do not interpret this as a safe status; check official local sources.";
    statusLocation.textContent    = "Location: \u2014";
    statusUpdated.textContent     = `Last attempt: ${new Date().toLocaleTimeString()}`;
    console.error("Aabhaas alert check failed:", error);
  }
}

refreshAlert();
setInterval(refreshAlert, POLL_INTERVAL_MS);
