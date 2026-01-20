
(() => {
  const KEY = "tm_theme";
  const root = document.documentElement;

// Function definition: reusable logic block

  // -------------------------------
  // Function block: read this as input -> processing -> output
  // -------------------------------
  function apply(theme){
    root.setAttribute("data-bs-theme", theme);
    try { localStorage.setItem(KEY, theme); } catch(e){}
  }

// Function definition: reusable logic block

  // -------------------------------
  // Function block: read this as input -> processing -> output
  // -------------------------------
  function getStored(){
    try { return localStorage.getItem(KEY); } catch(e){ return null; }
  }

  // boot
  const stored = getStored();
  // Control-flow: starts a 'if(stored' block
  if(stored === "dark" || stored === "light"){
    apply(stored);
  }

  // quick toggle (navbar button)
// DOM access: selecting HTML elements to read/update UI
  const btn = document.getElementById("quickTheme");
  // Control-flow: starts a 'if(btn){' block
  if(btn){
// Event listener: runs a function when the user triggers an event
    // Event listener: runs the callback when the event occurs
    btn.addEventListener("click", () => {
      const current = root.getAttribute("data-bs-theme") || "light";
      apply(current === "dark" ? "light" : "dark");
    });
  }

  // settings page toggle support
// DOM access: selecting HTML elements to read/update UI
  const settingsToggle = document.getElementById("themeToggle");
  // Control-flow: starts a 'if(settingsToggle){' block
  if(settingsToggle){
    const current = root.getAttribute("data-bs-theme") || "light";
    settingsToggle.checked = current === "dark";
// Event listener: runs a function when the user triggers an event
    // Event listener: runs the callback when the event occurs
    settingsToggle.addEventListener("change", async () => {
      const next = settingsToggle.checked ? "dark" : "light";
      apply(next);
      // best-effort persist to backend if endpoint exists
      // Control-flow: starts a 'try{' block
      try{
// Network request: fetch() calls an API endpoint and returns a Promise
        await fetch("/api/settings", {
          method:"POST",
          headers:{"Content-Type":"application/json"},
          body: JSON.stringify({ theme: next })
        });
      }catch(e){}
    });
  }
})();
