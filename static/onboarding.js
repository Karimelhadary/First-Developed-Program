// onboarding.js - visual mood selector and accessible behavior
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    const moods = document.querySelectorAll('.mood');
    moods.forEach(label => {
      const input = label.querySelector('input[type=radio]');
      if (!input) return;
      function updateClass() {
        if (input.checked) label.classList.add('active'); else label.classList.remove('active');
      }
      label.addEventListener('click', function () {
        input.checked = true;
        updateClass();
      });
      input.addEventListener('change', updateClass);
      updateClass();
    });
  });
})();
