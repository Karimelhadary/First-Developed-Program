// This JavaScript file manages the Pomodoro timer functionality.
// It handles focus sessions and transitions to breaks, with configurable durations.
// Supports different modes: focus, short break, long break, and tracks sessions.

// Global variable for the timer interval ID
let intervalId = null;
// Initial remaining seconds, default 25 minutes for focus
let remainingSeconds = 25 * 60;

// DOM elements for timer display and controls
// Element displaying the countdown time
const display = document.getElementById("timerDisplay");
// Element showing the current mode subtitle
const subtitle = document.getElementById("timerSubtitle");
// Button to start the timer
const startBtn = document.getElementById("startBtn");
// Button to pause the timer
const pauseBtn = document.getElementById("pauseBtn");
// Button to reset the timer
const resetBtn = document.getElementById("resetBtn");
// Select dropdown for choosing timer mode
const modeSelect = document.getElementById("modeSelect");
// Input field for custom minutes
const minutesInput = document.getElementById("minutesInput");
// Select dropdown for choosing associated task
const taskSelect = document.getElementById("taskSelect");
// Hidden element with configuration attributes
const configEl = document.getElementById("timerConfig");

// Function to read integer attributes from config element
function readIntAttr(name, fallback) {
  if (!configEl) return fallback;
  const raw = configEl.getAttribute(name);
  const n = parseInt(raw || "", 10);
  return Number.isFinite(n) ? n : fallback;
}

// Settings object with timer durations read from attributes
const SETTINGS = {
  focusMinutes: readIntAttr("data-focus-minutes", 25),
  breakMinutes: readIntAttr("data-break-minutes", 5),
  longBreakMinutes: readIntAttr("data-long-break-minutes", 15),
  sessionsBeforeLongBreak: readIntAttr("data-sessions-before-long-break", 4)
};

// Key for storing focus session count in localStorage
const STORAGE_KEY = "tm_focusCount";

// Function to format seconds into MM:SS string
function fmt(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, "0");
  const s = Math.floor(sec % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

// Function to clamp an integer value within min and max bounds
function clampInt(n, min, max, fallback) {
  const x = parseInt(n, 10);
  if (!Number.isFinite(x)) return fallback;
  return Math.max(min, Math.min(max, x));
}

// Function to get the display label for a timer mode
function modeLabel(mode) {
  if (mode === "break") return "Short break";
  if (mode === "long_break") return "Long break";
  return "Focus session";
}

// Function to get default minutes for a given mode
function modeDefaultMinutes(mode) {
  if (mode === "break") return SETTINGS.breakMinutes;
  if (mode === "long_break") return SETTINGS.longBreakMinutes;
  return SETTINGS.focusMinutes;
}

// Function to synchronize timer state from input controls
function syncFromInputs() {
  // Get current mode from select
  const mode = modeSelect?.value || "focus";
  // Clamp input minutes to valid range
  const mins = clampInt(minutesInput?.value, 1, 180, modeDefaultMinutes(mode));
  // Update input field with clamped value
  if (minutesInput) minutesInput.value = mins;

  // Calculate remaining seconds
  remainingSeconds = mins * 60;
  // Update display and subtitle
  if (display) display.textContent = fmt(remainingSeconds);
  if (subtitle) subtitle.textContent = modeLabel(mode);
}

// Function to retrieve focus count from localStorage
function getFocusCount() {
  const raw = localStorage.getItem(STORAGE_KEY);
  const n = parseInt(raw || "0", 10);
  return Number.isFinite(n) ? n : 0;
}

// Function to set focus count in localStorage
function setFocusCount(n) {
  localStorage.setItem(STORAGE_KEY, String(Math.max(0, n)));
}

// Asynchronous function to log a session to the server
async function logSession(mode, minutes, taskId) {
  // Determine API endpoint based on mode
  const endpoint = mode === "focus" ? "/api/focus-sessions" : "/api/break-sessions";
  // Prepare payload with minutes
  const payload = { minutes };
  // Add task ID if focus mode and task selected
  if (mode === "focus" && taskId) payload.task_id = taskId;
  // Add mode for break sessions
  if (mode !== "focus") payload.mode = mode;

  try {
    // Send POST request to log the session
    await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (e) {
    // Ignore errors to prevent UI crashes
  }
}

// Function to update UI button states based on running status
function setRunningUi(isRunning) {
  if (startBtn) startBtn.disabled = isRunning;
  if (pauseBtn) pauseBtn.disabled = !isRunning;
}

// Function to start the timer countdown
function start() {
  // Prevent multiple intervals
  if (intervalId) return;
  // Sync state from inputs
  syncFromInputs();
  // Update UI to running
  setRunningUi(true);

  // Start interval to decrement every second
  intervalId = setInterval(async () => {
    remainingSeconds -= 1;
    // Update display
    if (display) display.textContent = fmt(Math.max(0, remainingSeconds));

    // Check if timer finished
    if (remainingSeconds <= 0) {
      // Stop timer
      clearInterval(intervalId);
      intervalId = null;
      // Update UI
      setRunningUi(false);

      // Get current settings
      const mode = modeSelect?.value || "focus";
      const minutes = clampInt(minutesInput?.value, 1, 180, modeDefaultMinutes(mode));
      const taskId = taskSelect ? taskSelect.value : "";

      // Log the session
      await logSession(mode, minutes, taskId);

      // Handle mode transitions
      if (mode === "focus") {
        // Increment focus count
        const cycles = Math.max(1, SETTINGS.sessionsBeforeLongBreak);
        const newCount = getFocusCount() + 1;
        setFocusCount(newCount);

        // Determine if long break is due
        const isLongBreak = newCount % cycles === 0;
        const breakMode = isLongBreak ? "long_break" : "break";
        // Redirect to break page
        window.location.href = `/break?mode=${breakMode}`;
      } else {
        // After break, redirect back to timer
        window.location.href = "/timer";
      }
    }
  }, 1000);
}

// Function to pause the timer
function pause() {
  if (!intervalId) return;
  clearInterval(intervalId);
  intervalId = null;
  setRunningUi(false);
}

// Function to reset the timer
function reset() {
  pause();
  syncFromInputs();
}

// Event listener for mode select change
modeSelect?.addEventListener("change", () => {
  const mode = modeSelect.value;
  // Set default minutes for new mode
  minutesInput.value = modeDefaultMinutes(mode);
  syncFromInputs();
});

// Event listener for minutes input change
minutesInput?.addEventListener("change", syncFromInputs);

// Event listeners for buttons
startBtn?.addEventListener("click", start);
pauseBtn?.addEventListener("click", pause);
resetBtn?.addEventListener("click", reset);

// Initialize the timer on page load
syncFromInputs();
setRunningUi(false);
