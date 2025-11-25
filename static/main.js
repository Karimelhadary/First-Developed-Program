// static/main.js - site-wide behaviors: theme toggle and small helpers
(function () {
  // -------------------------------
  // THEME HANDLING (light / dark)
  // -------------------------------
  function applyTheme(theme, checkbox) {
    if (theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
      document.body.classList.add("dark");
      localStorage.setItem("theme", "dark");
      if (checkbox) checkbox.checked = true;
    } else {
      document.documentElement.removeAttribute("data-theme");
      document.body.classList.remove("dark");
      localStorage.setItem("theme", "light");
      if (checkbox) checkbox.checked = false;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    console.log("main.js loaded");

    // ----- Theme toggle -----
    const toggle = document.getElementById("theme-toggle");
    const saved = localStorage.getItem("theme");

    if (saved === "dark") {
      applyTheme("dark", toggle);
    } else if (saved === "light") {
      applyTheme("light", toggle);
    } else {
      // default theme based on checkbox (if present) or light
      applyTheme(toggle && toggle.checked ? "dark" : "light", toggle);
    }

    if (toggle) {
      toggle.addEventListener("change", function () {
        applyTheme(this.checked ? "dark" : "light", toggle);
      });
    }

    // -------------------------------
    // DASHBOARD MOOD CHIPS
    // -------------------------------
    const chips = document.querySelectorAll(".mood-bar .chip");
    if (chips.length) {
      chips.forEach((chip) => {
        chip.addEventListener("click", function () {
          chips.forEach((c) => c.classList.remove("active"));
          this.classList.add("active");
          // you could later also send this to the backend or update query params
          console.log("Mood chip selected:", this.innerText.trim());
        });
      });
    }

    // place any other global behaviors here later...
  });
})();
