
let intervalId = null;
let remainingSeconds = 5 * 60;

const display = document.getElementById("breakTimerDisplay");
const subtitle = document.getElementById("breakSubtitle");
const startBtn = document.getElementById("breakStartBtn");
const pauseBtn = document.getElementById("breakPauseBtn");
const resetBtn = document.getElementById("breakResetBtn");

function fmt(sec){
  const m = Math.floor(sec/60).toString().padStart(2,"0");
  const s = Math.floor(sec%60).toString().padStart(2,"0");
  return `${m}:${s}`;
}

function sync(){
  display.textContent = fmt(remainingSeconds);
}

async function logBreak(minutes){
  try{
    await fetch("/api/break-sessions", {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ minutes })
    });
  }catch(e){}
}

function start(){
  if(intervalId) return;
  startBtn.disabled = true;
  pauseBtn.disabled = false;

  intervalId = setInterval(async () => {
    remainingSeconds -= 1;
    sync();
    if(remainingSeconds <= 0){
      clearInterval(intervalId);
      intervalId = null;
      pauseBtn.disabled = true;
      startBtn.disabled = false;

      await logBreak(5);
      subtitle.textContent = "Break completed ✅";
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
  remainingSeconds = 5 * 60;
  subtitle.textContent = "Short break";
  sync();
}

startBtn?.addEventListener("click", start);
pauseBtn?.addEventListener("click", pause);
resetBtn?.addEventListener("click", reset);

sync();
