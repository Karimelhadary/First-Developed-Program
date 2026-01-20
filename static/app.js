
// This is static/app.js - handles theme management for the application
(() => {
  // Key for storing theme in localStorage
  const KEY = "tm_theme";
  // Reference to the root HTML element
  const root = document.documentElement;

  // Function to apply the theme to the document
  function apply(theme){
    // Set the data-bs-theme attribute on root
    root.setAttribute("data-bs-theme", theme);
    // Try to save to localStorage, ignore errors
    try { localStorage.setItem(KEY, theme); } catch(e){}
  }

  // Function to get the stored theme from localStorage
  function getStored(){
    // Try to get from localStorage, return null on error
    try { return localStorage.getItem(KEY); } catch(e){ return null; }
  }

  // On load, get stored theme
  const stored = getStored();
  // If stored theme is valid, apply it
  if(stored === "dark" || stored === "light"){
    apply(stored);
  }

  // Quick toggle button in navbar
  const btn = document.getElementById("quickTheme");
  // If button exists, add click listener
  if(btn){
    // On click, toggle between dark and light
    btn.addEventListener("click", () => {
      const current = root.getAttribute("data-bs-theme") || "light";
      apply(current === "dark" ? "light" : "dark");
    });
  }

  // Settings page toggle support
  const settingsToggle = document.getElementById("themeToggle");
  // If settings toggle exists
  if(settingsToggle){
    // Get current theme
    const current = root.getAttribute("data-bs-theme") || "light";
    // Set checkbox checked state based on current theme
    settingsToggle.checked = current === "dark";
    // Add change event listener to toggle
    settingsToggle.addEventListener("change", async () => {
      // Determine next theme based on checkbox
      const next = settingsToggle.checked ? "dark" : "light";
      // Apply the theme
      apply(next);
      // Try to persist to backend via API
      try{
        // Send POST request to /api/settings with theme
        await fetch("/api/settings", {
          method:"POST",
          headers:{"Content-Type":"application/json"},
          body: JSON.stringify({ theme: next })
        });
      }catch(e){}
    });
  }
})();
