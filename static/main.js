// main.js - site-wide behaviors: theme toggle and small helpers
(function () {
  function setTheme(dark) {
    if (dark) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
      const cb = document.getElementById('theme-toggle'); if(cb) cb.checked = true;
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'light');
      const cb = document.getElementById('theme-toggle'); if(cb) cb.checked = false;
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    // initialize theme
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') setTheme(true);

    // wire toggle
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      toggle.addEventListener('change', function () {
        setTheme(!!this.checked);
      });
    }

    // add small helper for external links (open in same tab) - placeholder
    // (other site-wide behaviors can be added here)
  });
})();
