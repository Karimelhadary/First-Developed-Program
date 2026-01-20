
// addtask.js - Provides helper functions for the add/edit task form.
// Specifically handles dynamic labels for range input sliders.

// Immediately invoked function expression (IIFE) to encapsulate code
(function () {
  // Function to attach a dynamic label to a range input showing its current value
  function attachRangeLabel(input) {
    if (!input) return;
    // Create a span element for the value label if it doesn't exist
    let span = input.parentNode.querySelector('.range-value');
    if (!span) {
      span = document.createElement('span');
      span.className = 'range-value';
      input.parentNode.appendChild(span);
    }

    // Function to update the label with the current input value
    function update() { span.textContent = input.value; }
    // Add event listener for input changes to update the label
    input.addEventListener('input', update);
    // Initial update to set the label
    update();
  }

  // Wait for DOM to load, then attach labels to all range inputs
  document.addEventListener('DOMContentLoaded', function () {
    const ranges = document.querySelectorAll('input[type="range"]');
    ranges.forEach(attachRangeLabel);
  });
})();
