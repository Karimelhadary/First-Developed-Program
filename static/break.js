// This JavaScript file handles the break timer functionality for the application.
// It manages a countdown timer for break periods, with options for short and long breaks.
// The timer can be started, paused, and reset, and logs break sessions to the server.

// Global variable to store the interval ID for the timer, allowing control over the countdown
let intervalId = null;

// DOM elements for displaying and controlling the break timer
// Element to display the remaining time in MM:SS format
const display = document.getElementById("breakTimerDisplay");
// Element to show the subtitle, like "Short break" or "Break completed"
const subtitle = document.getElementById("breakSubtitle");
// Button to start the timer
const startBtn = document.getElementById("breakStartBtn");
// Button to pause the timer
const pauseBtn = document.getElementById("breakPauseBtn");
// Button to reset the timer
const resetBtn = document.getElementById("breakResetBtn");
// Hidden element containing configuration data as attributes
const configEl = document.getElementById("breakConfig");

// Key for storing focus count in localStorage, used to track sessions
const STORAGE_KEY = "tm_focusCount";

// Function to read an integer attribute from the config element, with a fallback value
// Parameters: name - the attribute name, fallback - default value if not found or invalid
function readIntAttr(name, fallback) {
  // Check if config element exists
  if (!configEl) return fallback;
  // Get the raw attribute value
  const raw = configEl.getAttribute(name);
  // Parse it as integer
  const n = parseInt(raw || "", 10);
  // Return the number if finite, else fallback
  return Number.isFinite(n) ? n : fallback;
}

// Function to read a string attribute from the config element, with a fallback value
// Parameters: name - the attribute name, fallback - default value if not found
function readStrAttr(name, fallback) {
  // Check if config element exists
  if (!configEl) return fallback;
  // Return the attribute value or fallback
  return configEl.getAttribute(name) || fallback;
}

// Read break duration in minutes from data attribute, default 5
const BREAK_MINUTES = readIntAttr("data-break-minutes", 5);
// Read break mode from data attribute, default "break"
const BREAK_MODE = readStrAttr("data-break-mode", "break");
// Calculate total seconds for the break, ensuring at least 1 minute
let remainingSeconds = Math.max(1, BREAK_MINUTES) * 60;

// Function to format seconds into MM:SS string for display
function fmt(sec) {
  // Calculate minutes, convert to string and pad with zero to 2 digits
  const m = Math.floor(sec / 60).toString().padStart(2, "0");
  // Calculate seconds, convert to string and pad with zero to 2 digits
  const s = Math.floor(sec % 60).toString().padStart(2, "0");
  // Return formatted string
  return `${m}:${s}`;
}

// Function to update the display with the current remaining time
function sync() {
  // Set the text content of the display element to the formatted time
  if (display) display.textContent = fmt(Math.max(0, remainingSeconds));
}

// Function to enable/disable buttons based on whether timer is running
function setRunningUi(isRunning) {
  // Disable start button if running, enable if not
  if (startBtn) startBtn.disabled = isRunning;
  // Disable pause button if not running, enable if running
  if (pauseBtn) pauseBtn.disabled = !isRunning;
}

// Asynchronously log the break session to the server
async function logBreak(minutes, mode) {
  try {
    // Send POST request to the break sessions API endpoint
    await fetch("/api/break-sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ minutes, mode })
    });
  } catch (e) {
    // Ignore any errors that occur during logging
  }
}

// Function to start the countdown timer
function start() {
  // Prevent starting multiple intervals
  if (intervalId) return;
  // Update UI to indicate timer is running
  setRunningUi(true);

  // Set interval to decrement every second (1000ms)
  intervalId = setInterval(async () => {
    // Decrement remaining time by 1 second
    remainingSeconds -= 1;
    // Update the display
    sync();

    // Check if time is up
    if (remainingSeconds <= 0) {
      // Stop the timer
      clearInterval(intervalId);
      intervalId = null;
      // Update UI to stopped state
      setRunningUi(false);

      // Log the break session
      await logBreak(BREAK_MINUTES, BREAK_MODE);

      // Update subtitle to show completion
      if (subtitle) subtitle.textContent = "Break completed ✅";
      // Reset focus count if it was a long break
      if (BREAK_MODE === "long_break") {
        localStorage.setItem(STORAGE_KEY, "0");
      }
    }
  }, 1000);
}

// Function to pause the timer
function pause() {
  // If no interval is running, do nothing
  if (!intervalId) return;
  // Clear the interval to stop counting
  clearInterval(intervalId);
  intervalId = null;
  // Update UI to paused state
  setRunningUi(false);
}

// Function to reset the timer to initial state
function reset() {
  // Pause the timer first
  pause();
  // Reset remaining seconds to initial value
  remainingSeconds = Math.max(1, BREAK_MINUTES) * 60;
  // Set subtitle based on break mode
  if (subtitle) subtitle.textContent = BREAK_MODE === "long_break" ? "Long break" : "Short break";
  // Update the display
  sync();
}

// Event listeners for button clicks
// Attach start function to start button click
startBtn?.addEventListener("click", start);
// Attach pause function to pause button click
pauseBtn?.addEventListener("click", pause);
// Attach reset function to reset button click
resetBtn?.addEventListener("click", reset);

// Initialize the timer display on page load
reset();
