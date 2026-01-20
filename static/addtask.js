
// addtask.js - small helpers for the add/edit task form
(function () {
// Function definition: reusable logic block
  function attachRangeLabel(input) {
    if (!input) return;
    // create label next to range if not present
// DOM access: selecting HTML elements to read/update UI
    let span = input.parentNode.querySelector('.range-value');
    if (!span) {
      span = document.createElement('span');
      span.className = 'range-value';
      input.parentNode.appendChild(span);
    }
// Function definition: reusable logic block
    function update() { span.textContent = input.value; }
// Event listener: runs a function when the user triggers an event
    input.addEventListener('input', update);
    update();
  }

// Event listener: runs a function when the user triggers an event
  document.addEventListener('DOMContentLoaded', function () {
// DOM access: selecting HTML elements to read/update UI
    const ranges = document.querySelectorAll('input[type="range"]');
    ranges.forEach(attachRangeLabel);
  });
})();
