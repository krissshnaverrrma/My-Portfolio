document.addEventListener("DOMContentLoaded", function () {

  const revealElements = document.querySelectorAll('.glass-card, .btn-glass, h2, h4, .project-img-wrapper, .map-icon-container');

  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('reveal', 'active');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  revealElements.forEach(el => {
    el.classList.add('reveal'); 
    revealObserver.observe(el);
  });
});