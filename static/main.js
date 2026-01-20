
// static/main.js - site-wide behaviors: theme toggle and small helpers
(function () {
  // -------------------------------
  // THEME HANDLING (light / dark)
  // -------------------------------
// Function definition: reusable logic block

  // -------------------------------
  // Function block: read this as input -> processing -> output
  // -------------------------------
  function applyTheme(theme, checkbox) {
    // Control-flow: starts a 'if' block
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

// Event listener: runs a function when the user triggers an event
  // Event listener: runs the callback when the event occurs
  document.addEventListener("DOMContentLoaded", function () {
    console.log("main.js loaded");

    // ----- Theme toggle -----
// DOM access: selecting HTML elements to read/update UI
    const toggle = document.getElementById("theme-toggle");
    const saved = localStorage.getItem("theme");

    // Control-flow: starts a 'if' block
    if (saved === "dark") {
      applyTheme("dark", toggle);
    } else if (saved === "light") {
      applyTheme("light", toggle);
    } else {
      // default theme based on checkbox (if present) or light
      applyTheme(toggle && toggle.checked ? "dark" : "light", toggle);
    }

    // Control-flow: starts a 'if' block
    if (toggle) {
// Event listener: runs a function when the user triggers an event
      // Event listener: runs the callback when the event occurs
      toggle.addEventListener("change", function () {
        applyTheme(this.checked ? "dark" : "light", toggle);
      });
    }

    // -------------------------------
    // DASHBOARD MOOD CHIPS
    // -------------------------------
// DOM access: selecting HTML elements to read/update UI
    const chips = document.querySelectorAll(".mood-bar .chip");
    // Control-flow: starts a 'if' block
    if (chips.length) {
      chips.forEach((chip) => {
// Event listener: runs a function when the user triggers an event
        // Event listener: runs the callback when the event occurs
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
