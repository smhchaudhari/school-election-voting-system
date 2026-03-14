
(() => {
  const path = window.location.pathname;
  document.querySelectorAll('.navbar .nav-link').forEach(a => {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });
})();
