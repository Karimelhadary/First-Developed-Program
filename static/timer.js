
let intervalId = null;
let remainingSeconds = 25 * 60;

// DOM access: selecting HTML elements to read/update UI
const display = document.getElementById("timerDisplay");
// DOM access: selecting HTML elements to read/update UI
const subtitle = document.getElementById("timerSubtitle");
// DOM access: selecting HTML elements to read/update UI
const startBtn = document.getElementById("startBtn");
// DOM access: selecting HTML elements to read/update UI
const pauseBtn = document.getElementById("pauseBtn");
// DOM access: selecting HTML elements to read/update UI
const resetBtn = document.getElementById("resetBtn");
// DOM access: selecting HTML elements to read/update UI
const modeSelect = document.getElementById("modeSelect");
// DOM access: selecting HTML elements to read/update UI
const minutesInput = document.getElementById("minutesInput");
// DOM access: selecting HTML elements to read/update UI
const taskSelect = document.getElementById("taskSelect");
// DOM access: selecting HTML elements to read/update UI
const configEl = document.getElementById("timerConfig");

// Function definition: reusable logic block
function readIntAttr(name, fallback) {
  if (!configEl) return fallback;
  const raw = configEl.getAttribute(name);
  const n = parseInt(raw || "", 10);
  return Number.isFinite(n) ? n : fallback;
}

const SETTINGS = {
  focusMinutes: readIntAttr("data-focus-minutes", 25),
  breakMinutes: readIntAttr("data-break-minutes", 5),
  longBreakMinutes: readIntAttr("data-long-break-minutes", 15),
  sessionsBeforeLongBreak: readIntAttr("data-sessions-before-long-break", 4)
};

const STORAGE_KEY = "tm_focusCount";

// Function definition: reusable logic block
function fmt(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, "0");
  const s = Math.floor(sec % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

// Function definition: reusable logic block
function clampInt(n, min, max, fallback) {
  const x = parseInt(n, 10);
  if (!Number.isFinite(x)) return fallback;
  return Math.max(min, Math.min(max, x));
}

// Function definition: reusable logic block
function modeLabel(mode) {
  if (mode === "break") return "Short break";
  if (mode === "long_break") return "Long break";
  return "Focus session";
}

// Function definition: reusable logic block
function modeDefaultMinutes(mode) {
  if (mode === "break") return SETTINGS.breakMinutes;
  if (mode === "long_break") return SETTINGS.longBreakMinutes;
  return SETTINGS.focusMinutes;
}

// Function definition: reusable logic block
function syncFromInputs() {
  const mode = modeSelect?.value || "focus";
  const mins = clampInt(minutesInput?.value, 1, 180, modeDefaultMinutes(mode));
  if (minutesInput) minutesInput.value = mins;

  remainingSeconds = mins * 60;
  if (display) display.textContent = fmt(remainingSeconds);
  if (subtitle) subtitle.textContent = modeLabel(mode);
}

// Function definition: reusable logic block
function getFocusCount() {
  const raw = localStorage.getItem(STORAGE_KEY);
  const n = parseInt(raw || "0", 10);
  return Number.isFinite(n) ? n : 0;
}

// Function definition: reusable logic block
function setFocusCount(n) {
  localStorage.setItem(STORAGE_KEY, String(Math.max(0, n)));
}

async function logSession(mode, minutes, taskId) {
  const endpoint = mode === "focus" ? "/api/focus-sessions" : "/api/break-sessions";
  const payload = { minutes };
  if (mode === "focus" && taskId) payload.task_id = taskId;
  if (mode !== "focus") payload.mode = mode;

  try {
// Network request: fetch() calls an API endpoint and returns a Promise
    await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (e) {
    // ignore API errors so UI never crashes
  }
}

// Function definition: reusable logic block
function setRunningUi(isRunning) {
  if (startBtn) startBtn.disabled = isRunning;
  if (pauseBtn) pauseBtn.disabled = !isRunning;
}

// Function definition: reusable logic block
function start() {
  if (intervalId) return;
  syncFromInputs();
  setRunningUi(true);

  intervalId = setInterval(async () => {
    remainingSeconds -= 1;
    if (display) display.textContent = fmt(Math.max(0, remainingSeconds));

    if (remainingSeconds <= 0) {
      clearInterval(intervalId);
      intervalId = null;
      setRunningUi(false);

      const mode = modeSelect?.value || "focus";
      const minutes = clampInt(minutesInput?.value, 1, 180, modeDefaultMinutes(mode));
      const taskId = taskSelect ? taskSelect.value : "";

      await logSession(mode, minutes, taskId);

      if (mode === "focus") {
        const cycles = Math.max(1, SETTINGS.sessionsBeforeLongBreak);
        const newCount = getFocusCount() + 1;
        setFocusCount(newCount);

        const isLongBreak = newCount % cycles === 0;
        const breakMode = isLongBreak ? "long_break" : "break";
        window.location.href = `/break?mode=${breakMode}`;
      } else {
        window.location.href = "/timer";
      }
    }
  }, 1000);
}

// Function definition: reusable logic block
function pause() {
  if (!intervalId) return;
  clearInterval(intervalId);
  intervalId = null;
  setRunningUi(false);
}

// Function definition: reusable logic block
function reset() {
  pause();
  syncFromInputs();
}

// Event listener: runs a function when the user triggers an event
modeSelect?.addEventListener("change", () => {
  const mode = modeSelect.value;
  minutesInput.value = modeDefaultMinutes(mode);
  syncFromInputs();
});

// Event listener: runs a function when the user triggers an event
minutesInput?.addEventListener("change", syncFromInputs);

// Event listener: runs a function when the user triggers an event
startBtn?.addEventListener("click", start);
// Event listener: runs a function when the user triggers an event
pauseBtn?.addEventListener("click", pause);
// Event listener: runs a function when the user triggers an event
resetBtn?.addEventListener("click", reset);

syncFromInputs();
setRunningUi(false);
