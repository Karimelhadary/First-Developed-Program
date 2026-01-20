
// static/onboarding.js - mood selection interactions

// Event listener: runs a function when the user triggers an event
document.addEventListener("DOMContentLoaded", function () {
  console.log("onboarding.js loaded");

// DOM access: selecting HTML elements to read/update UI
  const moodLabels = document.querySelectorAll(".mood");
// DOM access: selecting HTML elements to read/update UI
  const selectedText = document.getElementById("mood-selected");

// Function definition: reusable logic block
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
// DOM access: selecting HTML elements to read/update UI
    const input = label.querySelector("input[type='radio']");
    if (!input) return;

    // initial active state
    if (input.checked) {
      label.classList.add("active");
      updateSelectedText(input.value);
    }

// Event listener: runs a function when the user triggers an event
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
