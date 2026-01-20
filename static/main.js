
// This is static/main.js - handles site-wide behaviors like theme toggle and small helpers
// Immediately invoked function expression (IIFE) to avoid polluting global scope
(function () {
  // Function to apply the selected theme (light or dark) to the page
  function applyTheme(theme, checkbox) {
    // If theme is dark, set data-theme attribute, add dark class, save to localStorage, check checkbox
    if (theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
      document.body.classList.add("dark");
      localStorage.setItem("theme", "dark");
      if (checkbox) checkbox.checked = true;
    } else {
      // Otherwise, remove data-theme attribute, remove dark class, save light to localStorage, uncheck checkbox
      document.documentElement.removeAttribute("data-theme");
      document.body.classList.remove("dark");
      localStorage.setItem("theme", "light");
      if (checkbox) checkbox.checked = false;
    }
  }

  // Add event listener for when the DOM is fully loaded
  document.addEventListener("DOMContentLoaded", function () {
    // Log that main.js has loaded
    console.log("main.js loaded");

    // Get the theme toggle checkbox element
    const toggle = document.getElementById("theme-toggle");
    // Get the saved theme from localStorage
    const saved = localStorage.getItem("theme");

    // If saved theme is dark, apply dark theme
    if (saved === "dark") {
      applyTheme("dark", toggle);
    } else if (saved === "light") {
      // If saved theme is light, apply light theme
      applyTheme("light", toggle);
    } else {
      // If no saved theme, apply theme based on checkbox state or default to light
      applyTheme(toggle && toggle.checked ? "dark" : "light", toggle);
    }

    // If toggle checkbox exists, add change event listener
    if (toggle) {
      // When checkbox changes, apply the corresponding theme
      toggle.addEventListener("change", function () {
        // If checked, apply dark theme; else light
        applyTheme(this.checked ? "dark" : "light", this);
      });
    }

    // Handle mood chips on dashboard
    const chips = document.querySelectorAll(".mood-bar .chip");
    // If mood chips exist, add click listeners
    if (chips.length) {
      // For each chip, add click event listener
      chips.forEach((chip) => {
        // When a chip is clicked, remove active class from all chips, add to this one
        chip.addEventListener("click", function () {
          chips.forEach((c) => c.classList.remove("active"));
          this.classList.add("active");
          // Log the selected mood (could be used to update backend or query params later)
          console.log("Mood chip selected:", this.innerText.trim());
        });
      });
    }

    // Placeholder for any other global behaviors
  });
})();
