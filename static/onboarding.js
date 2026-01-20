
// static/onboarding.js - Handles mood selection interactions on the onboarding page.
// Allows users to select their current mood, updates UI accordingly.

// Wait for DOM to load before executing script
document.addEventListener("DOMContentLoaded", function () {
  // Log to console for debugging
  console.log("onboarding.js loaded");

  // Select all mood label elements (containers for radio buttons)
  const moodLabels = document.querySelectorAll(".mood");
  // Select the element that displays the selected mood text
  const selectedText = document.getElementById("mood-selected");

  // Function to update the displayed selected mood text with emoji
  function updateSelectedText(value) {
    if (!selectedText) return;
    let label = "";
    // Switch statement to map mood values to labels with emojis
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
    // Update the inner HTML with the selected mood
    selectedText.innerHTML = `Selected mood: <strong>${label}</strong>`;
  }

  // Loop through each mood label
  moodLabels.forEach((label) => {
    // Find the radio input inside the label
    const input = label.querySelector("input[type='radio']");
    if (!input) return;

    // Check initial state: if radio is checked, make label active and update text
    if (input.checked) {
      label.classList.add("active");
      updateSelectedText(input.value);
    }

    // Add click event listener to the label
    label.addEventListener("click", () => {
      // Remove active class from all labels
      moodLabels.forEach((l) => l.classList.remove("active"));
      // Add active class to clicked label
      label.classList.add("active");
      // Check the radio button
      input.checked = true;
      // Update the selected text display
      updateSelectedText(input.value);
    });
  });
});
