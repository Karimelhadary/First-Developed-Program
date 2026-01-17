let intervalId = null;
let remainingSeconds = 25 * 60;

const display = document.getElementById("timerDisplay");
const subtitle = document.getElementById("timerSubtitle");
const startBtn = document.getElementById("startBtn");
const pauseBtn = document.getElementById("pauseBtn");
const resetBtn = document.getElementById("resetBtn");
const modeSelect = document.getElementById("modeSelect");
const minutesInput = document.getElementById("minutesInput");
const taskSelect = document.getElementById("taskSelect");
const configEl = document.getElementById("timerConfig");

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

function fmt(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, "0");
  const s = Math.floor(sec % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

function clampInt(n, min, max, fallback) {
  const x = parseInt(n, 10);
  if (!Number.isFinite(x)) return fallback;
  return Math.max(min, Math.min(max, x));
}

function modeLabel(mode) {
  if (mode === "break") return "Short break";
  if (mode === "long_break") return "Long break";
  return "Focus session";
}

function modeDefaultMinutes(mode) {
  if (mode === "break") return SETTINGS.breakMinutes;
  if (mode === "long_break") return SETTINGS.longBreakMinutes;
  return SETTINGS.focusMinutes;
}

function syncFromInputs() {
  const mode = modeSelect?.value || "focus";
  const mins = clampInt(minutesInput?.value, 1, 180, modeDefaultMinutes(mode));
  if (minutesInput) minutesInput.value = mins;

  remainingSeconds = mins * 60;
  if (display) display.textContent = fmt(remainingSeconds);
  if (subtitle) subtitle.textContent = modeLabel(mode);
}

function getFocusCount() {
  const raw = localStorage.getItem(STORAGE_KEY);
  const n = parseInt(raw || "0", 10);
  return Number.isFinite(n) ? n : 0;
}

function setFocusCount(n) {
  localStorage.setItem(STORAGE_KEY, String(Math.max(0, n)));
}

async function logSession(mode, minutes, taskId) {
  const endpoint = mode === "focus" ? "/api/focus-sessions" : "/api/break-sessions";
  const payload = { minutes };
  if (mode === "focus" && taskId) payload.task_id = taskId;
  if (mode !== "focus") payload.mode = mode;

  try {
    await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (e) {
    // ignore API errors so UI never crashes
  }
}

function setRunningUi(isRunning) {
  if (startBtn) startBtn.disabled = isRunning;
  if (pauseBtn) pauseBtn.disabled = !isRunning;
}

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

function pause() {
  if (!intervalId) return;
  clearInterval(intervalId);
  intervalId = null;
  setRunningUi(false);
}

function reset() {
  pause();
  syncFromInputs();
}

modeSelect?.addEventListener("change", () => {
  const mode = modeSelect.value;
  minutesInput.value = modeDefaultMinutes(mode);
  syncFromInputs();
});

minutesInput?.addEventListener("change", syncFromInputs);

startBtn?.addEventListener("click", start);
pauseBtn?.addEventListener("click", pause);
resetBtn?.addEventListener("click", reset);

syncFromInputs();
setRunningUi(false);
