let intervalId = null;

const display = document.getElementById("breakTimerDisplay");
const subtitle = document.getElementById("breakSubtitle");
const startBtn = document.getElementById("breakStartBtn");
const pauseBtn = document.getElementById("breakPauseBtn");
const resetBtn = document.getElementById("breakResetBtn");
const configEl = document.getElementById("breakConfig");

const STORAGE_KEY = "tm_focusCount";

function readIntAttr(name, fallback) {
  if (!configEl) return fallback;
  const raw = configEl.getAttribute(name);
  const n = parseInt(raw || "", 10);
  return Number.isFinite(n) ? n : fallback;
}

function readStrAttr(name, fallback) {
  if (!configEl) return fallback;
  return configEl.getAttribute(name) || fallback;
}

const BREAK_MINUTES = readIntAttr("data-break-minutes", 5);
const BREAK_MODE = readStrAttr("data-break-mode", "break");

let remainingSeconds = Math.max(1, BREAK_MINUTES) * 60;

function fmt(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, "0");
  const s = Math.floor(sec % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

function sync() {
  if (display) display.textContent = fmt(Math.max(0, remainingSeconds));
}

function setRunningUi(isRunning) {
  if (startBtn) startBtn.disabled = isRunning;
  if (pauseBtn) pauseBtn.disabled = !isRunning;
}

async function logBreak(minutes, mode) {
  try {
    await fetch("/api/break-sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ minutes, mode })
    });
  } catch (e) {
    // ignore
  }
}

function start() {
  if (intervalId) return;
  setRunningUi(true);

  intervalId = setInterval(async () => {
    remainingSeconds -= 1;
    sync();

    if (remainingSeconds <= 0) {
      clearInterval(intervalId);
      intervalId = null;
      setRunningUi(false);

      await logBreak(BREAK_MINUTES, BREAK_MODE);

      if (subtitle) subtitle.textContent = "Break completed ✅";
      if (BREAK_MODE === "long_break") {
        localStorage.setItem(STORAGE_KEY, "0");
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
  remainingSeconds = Math.max(1, BREAK_MINUTES) * 60;
  if (subtitle) subtitle.textContent = BREAK_MODE === "long_break" ? "Long break" : "Short break";
  sync();
}

startBtn?.addEventListener("click", start);
pauseBtn?.addEventListener("click", pause);
resetBtn?.addEventListener("click", reset);

reset();
