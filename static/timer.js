// static/timer.js
// Simple 25-minute countdown timer with Start / Pause / Reset

(function () {
  document.addEventListener("DOMContentLoaded", function () {
    const display = document.getElementById("time");
    if (!display) {
      // Not on the timer page
      return;
    }

    const startBtn = document.getElementById("start-btn");
    const pauseBtn = document.getElementById("pause-btn");
    const resetBtn = document.getElementById("reset-btn");

    // 25 minutes in seconds
    const DEFAULT_DURATION = 25 * 60;
    let remaining = DEFAULT_DURATION;
    let timerId = null;
    let isRunning = false;

    function formatTime(seconds) {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      const mStr = mins.toString().padStart(2, "0");
      const sStr = secs.toString().padStart(2, "0");
      return `${mStr}:${sStr}`;
    }

    function render() {
      display.textContent = formatTime(remaining);
    }

    function tick() {
      if (remaining > 0) {
        remaining -= 1;
        render();
      } else {
        // time's up
        clearInterval(timerId);
        timerId = null;
        isRunning = false;
        alert("Time's up! Great job focusing ✨");
      }
    }

    function startTimer() {
      if (isRunning) return;
      isRunning = true;
      // update first so it doesn't wait 1 second before changing
      render();
      timerId = setInterval(tick, 1000);
    }

    function pauseTimer() {
      if (!isRunning) return;
      isRunning = false;
      if (timerId) {
        clearInterval(timerId);
        timerId = null;
      }
    }

    function resetTimer() {
      isRunning = false;
      if (timerId) {
        clearInterval(timerId);
        timerId = null;
      }
      remaining = DEFAULT_DURATION;
      render();
    }

    // Wire up buttons (if they exist)
    if (startBtn) startBtn.addEventListener("click", startTimer);
    if (pauseBtn) pauseBtn.addEventListener("click", pauseTimer);
    if (resetBtn) resetBtn.addEventListener("click", resetTimer);

    // Initial display
    render();
  });
})();
