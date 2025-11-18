// timer.js - simple focus timer (client-side only)
;(function () {
  let intervalId = null;
  let remaining = 25 * 60; // default 25 minutes

  function formatTime(sec) {
    const m = Math.floor(sec / 60).toString().padStart(2, '0');
    const s = (sec % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }

  function updateDisplay() {
    const el = document.getElementById('time');
    if (el) el.textContent = formatTime(remaining);
  }

  function start() {
    if (intervalId) return;
    intervalId = setInterval(() => {
      if (remaining > 0) {
        remaining -= 1;
        updateDisplay();
      } else {
        clearInterval(intervalId);
        intervalId = null;
        // optional: play sound or notify
      }
    }, 1000);
  }

  function pause() {
    if (intervalId) { clearInterval(intervalId); intervalId = null; }
  }

  function reset() {
    pause();
    remaining = 25 * 60;
    updateDisplay();
  }

  document.addEventListener('DOMContentLoaded', function () {
    updateDisplay();
    const startBtn = document.querySelector('.controls .btn');
    const pauseBtn = document.querySelector('.controls .btn.ghost');
    const resetBtn = document.querySelector('.controls .btn.ghost:last-of-type');

    if (startBtn) startBtn.addEventListener('click', start);
    if (pauseBtn) pauseBtn.addEventListener('click', pause);
    if (resetBtn) resetBtn.addEventListener('click', reset);
  });
})();
