// addtask.js - small helpers for the add/edit task form
(function () {
  function attachRangeLabel(input) {
    if (!input) return;
    // create label next to range if not present
    let span = input.parentNode.querySelector('.range-value');
    if (!span) {
      span = document.createElement('span');
      span.className = 'range-value';
      input.parentNode.appendChild(span);
    }
    function update() { span.textContent = input.value; }
    input.addEventListener('input', update);
    update();
  }

  document.addEventListener('DOMContentLoaded', function () {
    const ranges = document.querySelectorAll('input[type="range"]');
    ranges.forEach(attachRangeLabel);
  });
})();
