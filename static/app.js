
(() => {
  const KEY = "tm_theme";
  const root = document.documentElement;

  function apply(theme){
    root.setAttribute("data-bs-theme", theme);
    try { localStorage.setItem(KEY, theme); } catch(e){}
  }

  function getStored(){
    try { return localStorage.getItem(KEY); } catch(e){ return null; }
  }

  // boot
  const stored = getStored();
  if(stored === "dark" || stored === "light"){
    apply(stored);
  }

  // quick toggle (navbar button)
  const btn = document.getElementById("quickTheme");
  if(btn){
    btn.addEventListener("click", () => {
      const current = root.getAttribute("data-bs-theme") || "light";
      apply(current === "dark" ? "light" : "dark");
    });
  }

  // settings page toggle support
  const settingsToggle = document.getElementById("themeToggle");
  if(settingsToggle){
    const current = root.getAttribute("data-bs-theme") || "light";
    settingsToggle.checked = current === "dark";
    settingsToggle.addEventListener("change", async () => {
      const next = settingsToggle.checked ? "dark" : "light";
      apply(next);
      // best-effort persist to backend if endpoint exists
      try{
        await fetch("/api/settings", {
          method:"POST",
          headers:{"Content-Type":"application/json"},
          body: JSON.stringify({ theme: next })
        });
      }catch(e){}
    });
  }
})();
