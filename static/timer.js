
let intervalId = null;
let remainingSeconds = 25 * 60;

const display = document.getElementById("timerDisplay");
const subtitle = document.getElementById("timerSubtitle");
const startBtn = document.getElementById("startBtn");
const pauseBtn = document.getElementById("pauseBtn");
const resetBtn = document.getElementById("resetBtn");
const modeSelect = document.getElementById("modeSelect");
const minutesInput = document.getElementById("minutesInput");
const taskSelect = document.getElementById("taskSelect");

function fmt(sec){
  const m = Math.floor(sec/60).toString().padStart(2,"0");
  const s = Math.floor(sec%60).toString().padStart(2,"0");
  return `${m}:${s}`;
}

function modeDefaults(mode){
  // Try to infer reasonable defaults from the current minutesInput:
  // focus minutes already in the field; break = 5; long break = 15.
  if(mode === "break") return 5;
  if(mode === "long_break") return 15;
  return parseInt(minutesInput.value || "25", 10);
}

function syncFromInputs(){
  const mins = parseInt(minutesInput.value || "25", 10);
  remainingSeconds = Math.max(1, mins) * 60;
  display.textContent = fmt(remainingSeconds);

  const mode = modeSelect.value;
  subtitle.textContent = mode === "focus" ? "Focus session" : (mode === "break" ? "Short break" : "Long break");
}

async function logSession(mode, minutes, taskId){
  const endpoint = mode === "focus" ? "/api/focus-sessions" : "/api/break-sessions";
  const payload = { minutes: minutes };
  if(mode === "focus" && taskId) payload.task_id = taskId;

  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  // don't crash UI if API errors
  try { return await res.json(); } catch(e){ return null; }
}

function start(){
  if(intervalId) return;
  startBtn.disabled = true;
  pauseBtn.disabled = false;

  intervalId = setInterval(async () => {
    remainingSeconds -= 1;
    display.textContent = fmt(remainingSeconds);

    if(remainingSeconds <= 0){
      clearInterval(intervalId);
      intervalId = null;
      pauseBtn.disabled = true;
      startBtn.disabled = false;

      const mode = modeSelect.value;
      const minutes = parseInt(minutesInput.value || "25", 10);
      const taskId = taskSelect ? taskSelect.value : "";

      await logSession(mode, minutes, taskId);

      // after focus -> break page
      if(mode === "focus"){
        window.location.href = "/break";
      }else{
        // after break -> timer page
        window.location.href = "/timer";
      }
    }
  }, 1000);
}

function pause(){
  if(!intervalId) return;
  clearInterval(intervalId);
  intervalId = null;
  startBtn.disabled = false;
  pauseBtn.disabled = true;
}

function reset(){
  pause();
  syncFromInputs();
}

modeSelect?.addEventListener("change", () => {
  minutesInput.value = modeDefaults(modeSelect.value);
  syncFromInputs();
});
minutesInput?.addEventListener("change", syncFromInputs);

startBtn?.addEventListener("click", start);
pauseBtn?.addEventListener("click", pause);
resetBtn?.addEventListener("click", reset);

// init
syncFromInputs();
