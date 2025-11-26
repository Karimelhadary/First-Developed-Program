// static/onboarding.js - mood selection interactions

document.addEventListener("DOMContentLoaded", function () {
  console.log("onboarding.js loaded");

  const moodLabels = document.querySelectorAll(".mood");
  const selectedText = document.getElementById("mood-selected");

  function updateSelectedText(value) {
    if (!selectedText) return;
    let label = "";
    switch (value) {
      case "energetic":
        label = "energetic ⚡";
        break;
      case "focused":
        label = "focused 🎯";
        break;
      case "calm":
        label = "calm 😊";
        break;
      case "creative":
        label = "creative ✨";
        break;
      default:
        label = value;
    }
    selectedText.innerHTML = `Selected mood: <strong>${label}</strong>`;
  }

  moodLabels.forEach((label) => {
    const input = label.querySelector("input[type='radio']");
    if (!input) return;

    // initial active state
    if (input.checked) {
      label.classList.add("active");
      updateSelectedText(input.value);
    }

    label.addEventListener("click", () => {
      // clear all active
      moodLabels.forEach((l) => l.classList.remove("active"));
      // set this as active
      label.classList.add("active");
      input.checked = true;
      updateSelectedText(input.value);
    });
  });
});
