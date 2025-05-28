// static/js/admin/admin.js
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar toasts
    const toastElList = document.querySelectorAll('.toast');
    toastElList.forEach(el => {
        new bootstrap.Toast(el, { delay: 5000, autohide: true }).show();
    });
    
    // Bloquear navegación con flechas
    history.pushState(null, null, location.href);
    window.onpopstate = function(event) {
        history.go(1);
    };
    
    // Limpiar historial
    if(window.history.replaceState) {
        window.history.replaceState(null, null, window.location.href);
    }
    
    // Toggle sidebar
    const toggleBtn = document.getElementById('toggleSidebar');
    if(toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            document.querySelector('.admin-sidebar').classList.toggle('collapsed');
        });
    }
    
    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if(darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', 
                document.body.classList.contains('dark-mode') ? 'enabled' : 'disabled');
        });
        
        // Cargar preferencia guardada
        if(localStorage.getItem('darkMode') === 'enabled') {
            document.body.classList.add('dark-mode');
        }
    }
});