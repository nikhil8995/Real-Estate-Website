// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Example: Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.flashes li').forEach(function(el) {
            el.style.display = 'none';
        });
    }, 5000);
});
