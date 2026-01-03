// static/break.js
// Simple break timer that loads default break minutes from /api/settings and
// logs completion via POST /api/break-sessions.

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
    const display = document.getElementById('break-time');
    if (!display) return;

    const startBtn = document.getElementById('break-start');
    const pauseBtn = document.getElementById('break-pause');
    const resetBtn = document.getElementById('break-reset');

    let defaults = { break_minutes: 5 };
    try {
      defaults = await getJSON('/api/settings');
    } catch (e) {
      console.warn(e);
    }

    let remaining = (parseInt(defaults.break_minutes || 5, 10) || 5) * 60;
    let timerId = null;
    let isRunning = false;

    function render() {
      display.textContent = formatTime(remaining);
    }

    async function onComplete() {
      if (timerId) {
        clearInterval(timerId);
        timerId = null;
      }
      isRunning = false;
      const minutes = Math.max(1, Math.round(remaining / 60));
      try {
        await postJSON('/api/break-sessions', { minutes: parseInt(defaults.break_minutes || 5, 10), mode: 'short_break' });
      } catch (e) {
        console.error(e);
      }
      alert('Break finished ✅ Ready to focus?');
    }

    function tick() {
      if (remaining > 0) {
        remaining -= 1;
        render();
      } else {
        onComplete();
      }
    }

    function start() {
      if (isRunning) return;
      isRunning = true;
      timerId = setInterval(tick, 1000);
    }

    function pause() {
      if (!isRunning) return;
      isRunning = false;
      if (timerId) {
        clearInterval(timerId);
        timerId = null;
      }
    }

    function reset() {
      pause();
      remaining = (parseInt(defaults.break_minutes || 5, 10) || 5) * 60;
      render();
    }

    startBtn.addEventListener('click', start);
    pauseBtn.addEventListener('click', pause);
    resetBtn.addEventListener('click', reset);

    render();
  });
})();
