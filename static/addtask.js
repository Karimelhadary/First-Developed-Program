
// addtask.js - small helpers for the add/edit task form
(function () {
// Function definition: reusable logic block

  // -------------------------------
  // Function block: read this as input -> processing -> output
  // -------------------------------
  function attachRangeLabel(input) {
    if (!input) return;
    // create label next to range if not present
// DOM access: selecting HTML elements to read/update UI
    let span = input.parentNode.querySelector('.range-value');
    // Control-flow: starts a 'if' block
    if (!span) {
      span = document.createElement('span');
      span.className = 'range-value';
      input.parentNode.appendChild(span);
    }
// Function definition: reusable logic block

    // -------------------------------
    // Function block: read this as input -> processing -> output
    // -------------------------------
    function update() { span.textContent = input.value; }
// Event listener: runs a function when the user triggers an event
    // Event listener: runs the callback when the event occurs
    input.addEventListener('input', update);
    update();
  }

// Event listener: runs a function when the user triggers an event
  // Event listener: runs the callback when the event occurs
  document.addEventListener('DOMContentLoaded', function () {
// DOM access: selecting HTML elements to read/update UI
    const ranges = document.querySelectorAll('input[type="range"]');
    ranges.forEach(attachRangeLabel);
  });
})();
