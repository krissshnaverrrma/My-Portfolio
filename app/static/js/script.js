function updateStatusIndicator(status) {
    const dot = document.querySelector('.status-indicator');
    if (!dot) return;
    const statusMap = {
        'online': 'online',
        'database_mode': 'database',
        'database': 'database',
        'offline': 'offline'
    };
    const targetClass = statusMap[status] || 'offline';
    dot.classList.remove('online', 'database', 'offline');
    dot.classList.add(targetClass);
}
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