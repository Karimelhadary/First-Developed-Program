// static/timer.js - simple 25-minute focus timer

document.addEventListener("DOMContentLoaded", function () {
  // This alert is just to prove the JS is running.
  // Once you see it, we can remove it if you want.
  console.log("timer.js loaded and DOM ready");
  // alert("timer.js loaded");  // uncomment this line if you want a popup check

  const DURATION = 25 * 60; // 25 minutes in seconds
  let remaining = DURATION;
  let intervalId = null;

  const timeEl = document.getElementById("time");
  const startBtn = document.getElementById("startBtn");
  const pauseBtn = document.getElementById("pauseBtn");
  const resetBtn = document.getElementById("resetBtn");

  function formatTime(sec) {
    const m = Math.floor(sec / 60).toString().padStart(2, "0");
    const s = (sec % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  }

  function updateDisplay() {
    if (timeEl) {
      timeEl.textContent = formatTime(remaining);
    }
  }

  function tick() {
    if (remaining > 0) {
      remaining -= 1;
      updateDisplay();
    } else {
      clearInterval(intervalId);
      intervalId = null;
      alert("Time's up! Great job staying focused ✨");
    }
  }

  function startTimer() {
    console.log("Start clicked");
    if (intervalId !== null) return; // already running
    intervalId = setInterval(tick, 1000);
  }

  function pauseTimer() {
    console.log("Pause clicked");
    if (intervalId !== null) {
      clearInterval(intervalId);
      intervalId = null;
    }
  }

  function resetTimer() {
    console.log("Reset clicked");
    pauseTimer();
    remaining = DURATION;
    updateDisplay();
  }

  // attach events
  if (startBtn) startBtn.addEventListener("click", startTimer);
  if (pauseBtn) pauseBtn.addEventListener("click", pauseTimer);
  if (resetBtn) resetBtn.addEventListener("click", resetTimer);

  // initial display
  updateDisplay();
});
