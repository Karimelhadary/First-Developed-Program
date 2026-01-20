
let intervalId = null;

// DOM access: selecting HTML elements to read/update UI
const display = document.getElementById("breakTimerDisplay");
// DOM access: selecting HTML elements to read/update UI
const subtitle = document.getElementById("breakSubtitle");
// DOM access: selecting HTML elements to read/update UI
const startBtn = document.getElementById("breakStartBtn");
// DOM access: selecting HTML elements to read/update UI
const pauseBtn = document.getElementById("breakPauseBtn");
// DOM access: selecting HTML elements to read/update UI
const resetBtn = document.getElementById("breakResetBtn");
// DOM access: selecting HTML elements to read/update UI
const configEl = document.getElementById("breakConfig");

const STORAGE_KEY = "tm_focusCount";

// Function definition: reusable logic block

// -------------------------------
// Function block: read this as input -> processing -> output
// -------------------------------
function readIntAttr(name, fallback) {
  if (!configEl) return fallback;
  const raw = configEl.getAttribute(name);
  const n = parseInt(raw || "", 10);
  return Number.isFinite(n) ? n : fallback;
}

// Function definition: reusable logic block

// -------------------------------
// Function block: read this as input -> processing -> output
// -------------------------------
function readStrAttr(name, fallback) {
  if (!configEl) return fallback;
  return configEl.getAttribute(name) || fallback;
}

const BREAK_MINUTES = readIntAttr("data-break-minutes", 5);
const BREAK_MODE = readStrAttr("data-break-mode", "break");

let remainingSeconds = Math.max(1, BREAK_MINUTES) * 60;

// Function definition: reusable logic block

// -------------------------------
// Function block: read this as input -> processing -> output
// -------------------------------
function fmt(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, "0");
  const s = Math.floor(sec % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

// Function definition: reusable logic block

// -------------------------------
// Function block: read this as input -> processing -> output
// -------------------------------
function sync() {
  if (display) display.textContent = fmt(Math.max(0, remainingSeconds));
}

// Function definition: reusable logic block

// -------------------------------
// Function block: read this as input -> processing -> output
// -------------------------------
function setRunningUi(isRunning) {
  if (startBtn) startBtn.disabled = isRunning;
  if (pauseBtn) pauseBtn.disabled = !isRunning;
}

async function logBreak(minutes, mode) {
  // Control-flow: starts a 'try' block
  try {
// Network request: fetch() calls an API endpoint and returns a Promise
    await fetch("/api/break-sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ minutes, mode })
    });
  } catch (e) {
    // ignore
  }
}

// Function definition: reusable logic block

// -------------------------------
// Function block: read this as input -> processing -> output
// -------------------------------
function start() {
  if (intervalId) return;
  setRunningUi(true);

  intervalId = setInterval(async () => {
    remainingSeconds -= 1;
    sync();

    // Control-flow: starts a 'if' block
    if (remainingSeconds <= 0) {
      clearInterval(intervalId);
      intervalId = null;
      setRunningUi(false);

      await logBreak(BREAK_MINUTES, BREAK_MODE);

      if (subtitle) subtitle.textContent = "Break completed ✅";
      // Control-flow: starts a 'if' block
      if (BREAK_MODE === "long_break") {
        localStorage.setItem(STORAGE_KEY, "0");
      }
    }
  }, 1000);
}

// Function definition: reusable logic block

// -------------------------------
// Function block: read this as input -> processing -> output
// -------------------------------
function pause() {
  if (!intervalId) return;
  clearInterval(intervalId);
  intervalId = null;
  setRunningUi(false);
}

// Function definition: reusable logic block

// -------------------------------
// Function block: read this as input -> processing -> output
// -------------------------------
function reset() {
  pause();
  remainingSeconds = Math.max(1, BREAK_MINUTES) * 60;
  if (subtitle) subtitle.textContent = BREAK_MODE === "long_break" ? "Long break" : "Short break";
  sync();
}

// Event listener: runs a function when the user triggers an event
// Event listener: runs the callback when the event occurs
startBtn?.addEventListener("click", start);
// Event listener: runs a function when the user triggers an event
// Event listener: runs the callback when the event occurs
pauseBtn?.addEventListener("click", pause);
// Event listener: runs a function when the user triggers an event
// Event listener: runs the callback when the event occurs
resetBtn?.addEventListener("click", reset);

reset();
