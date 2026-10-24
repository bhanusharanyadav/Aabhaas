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
}

dismissButton.addEventListener("click", () => {
  if (lastPopupAlertId) dismissedAlertIds.add(lastPopupAlertId);
  modal.hidden = true;
});

async function refreshAlert() {
  try {
    if (!API_BASE || API_BASE.includes("YOUR_API_URL")) throw new Error("API URL is not configured.");
    const response = await fetch(`${API_BASE}/api/alerts/active`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Alert API returned HTTP ${response.status}.`);
    const payload = await response.json();
    connectionState.textContent = "Connected · checking every 5 seconds";
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
      statusIcon.textContent = "✓";
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
    statusLocation.textContent = "Location: —";
    statusUpdated.textContent = `Last attempt: ${new Date().toLocaleTimeString()}`;
    console.error("Aabhaas alert check failed:", error);
  }
}

refreshAlert();
setInterval(refreshAlert, POLL_INTERVAL_MS);
