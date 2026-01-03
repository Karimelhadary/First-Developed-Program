// static/timer.js
// Pomodoro-like timer with:
// - Custom duration + mode
// - Auto-save completed sessions via POST /api/focus-sessions or /api/break-sessions
// - Uses GET /api/settings to preload default minutes
// - Bootstrap modal when a focus session ends

(function () {
  async function getJSON(url) {
    const res = await fetch(url, { credentials: 'same-origin' });
    if (!res.ok) throw new Error('Request failed: ' + res.status);
    return res.json();
  }

  async function postJSON(url, payload) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Request failed: ' + res.status);
    return res.json();
  }

  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
  }

  document.addEventListener('DOMContentLoaded', async function () {
    const display = document.getElementById('time');
    if (!display) return;

    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const resetBtn = document.getElementById('reset-btn');

    const modeSelect = document.getElementById('mode-select');
    const minutesInput = document.getElementById('minutes-input');
    const taskIdInput = document.getElementById('task-id-input');
    const sessionLabel = document.getElementById('session-label');

    let defaults = { focus_minutes: 25, break_minutes: 5, long_break_minutes: 15 };
    try {
      defaults = await getJSON('/api/settings');
    } catch (e) {
      // If settings endpoint fails, we just use defaults.
      console.warn(e);
    }

    function applyDefaults(mode) {
      if (mode === 'focus') minutesInput.value = defaults.focus_minutes;
      else if (mode === 'short_break') minutesInput.value = defaults.break_minutes;
      else minutesInput.value = defaults.long_break_minutes;
    }

    // Initial defaults
    applyDefaults(modeSelect.value);

    let remaining = parseInt(minutesInput.value, 10) * 60;
    let timerId = null;
    let isRunning = false;

    function render() {
      display.textContent = formatTime(remaining);
      const mode = modeSelect.value;
      sessionLabel.textContent = mode === 'focus' ? 'Focus session' : (mode === 'short_break' ? 'Short break' : 'Long break');
    }

    function syncRemainingFromInput() {
      const mins = Math.max(1, Math.min(180, parseInt(minutesInput.value || '25', 10)));
      remaining = mins * 60;
      render();
    }

    async function onComplete() {
      // Prevent double complete
      if (timerId) {
        clearInterval(timerId);
        timerId = null;
      }
      isRunning = false;

      const mode = modeSelect.value;
      const minutes = Math.max(1, parseInt(minutesInput.value || '25', 10));

      try {
        if (mode === 'focus') {
          await postJSON('/api/focus-sessions', {
            minutes,
            mode: 'focus',
            task_id: (taskIdInput && taskIdInput.value || '').trim() || null
          });

          // Show bootstrap modal if present
          const modalEl = document.getElementById('doneModal');
          if (modalEl && window.bootstrap) {
            const m = new window.bootstrap.Modal(modalEl);
            m.show();
          } else {
            alert("Session saved. Time for a break!");
          }
        } else {
          await postJSON('/api/break-sessions', {
            minutes,
            mode: mode
          });
          alert('Break logged. Ready to focus again?');
        }
      } catch (e) {
        console.error(e);
        alert('Session finished, but saving failed. Check server console.');
      }
    }

    function tick() {
      if (remaining > 0) {
        remaining -= 1;
        render();
      } else {
        onComplete();
      }
    }

    function startTimer() {
      if (isRunning) return;
      isRunning = true;
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
      pauseTimer();
      syncRemainingFromInput();
    }

    // UI events
    startBtn.addEventListener('click', startTimer);
    pauseBtn.addEventListener('click', pauseTimer);
    resetBtn.addEventListener('click', resetTimer);

    modeSelect.addEventListener('change', function () {
      pauseTimer();
      applyDefaults(modeSelect.value);
      syncRemainingFromInput();
    });

    minutesInput.addEventListener('change', function () {
      if (!isRunning) syncRemainingFromInput();
    });

    // Initial
    syncRemainingFromInput();
  });
})();
