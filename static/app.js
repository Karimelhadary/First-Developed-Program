

(() => {
  const KEY = "tm_theme";
  const root = document.documentElement;

// Function definition: reusable logic block
  function apply(theme){
    root.setAttribute("data-bs-theme", theme);
    try { localStorage.setItem(KEY, theme); } catch(e){}
  }

// Function definition: reusable logic block
  function getStored(){
    try { return localStorage.getItem(KEY); } catch(e){ return null; }
  }

  // boot
  const stored = getStored();
  if(stored === "dark" || stored === "light"){
    apply(stored);
  }

  // quick toggle (navbar button)
// DOM access: selecting HTML elements to read/update UI
  const btn = document.getElementById("quickTheme");
  if(btn){
// Event listener: runs a function when the user triggers an event
    btn.addEventListener("click", () => {
      const current = root.getAttribute("data-bs-theme") || "light";
      apply(current === "dark" ? "light" : "dark");
    });
  }

  // settings page toggle support
// DOM access: selecting HTML elements to read/update UI
  const settingsToggle = document.getElementById("themeToggle");
  if(settingsToggle){
    const current = root.getAttribute("data-bs-theme") || "light";
    settingsToggle.checked = current === "dark";
// Event listener: runs a function when the user triggers an event
    settingsToggle.addEventListener("change", async () => {
      const next = settingsToggle.checked ? "dark" : "light";
      apply(next);
      // best-effort persist to backend if endpoint exists
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
