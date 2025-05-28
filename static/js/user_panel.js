// Toggle sidebar
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const mainContent = document.getElementById('mainContent');
const menuToggle = document.getElementById('menuToggle');

// Toggle sidebar collapse/expand
sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    
    // Ajuste para móviles
    if (window.innerWidth <= 992) {
        if (sidebar.classList.contains('collapsed')) {
            sidebar.classList.add('active');
        } else {
            sidebar.classList.remove('active');
        }
    }
});

// Toggle sidebar on mobile
menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('active');
    
    // Si está colapsado, alternar entre colapsado y expandido
    if (sidebar.classList.contains('collapsed') && sidebar.classList.contains('active')) {
        sidebar.classList.remove('collapsed');
    } else if (!sidebar.classList.contains('collapsed') && sidebar.classList.contains('active')) {
        // No hacer nada - ya está expandido
    }
});

// Cerrar sidebar al hacer clic fuera en móviles
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 992 && sidebar.classList.contains('active')) {
        if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    }
});

// Dark mode toggle
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;

// Check for saved dark mode preference
if (localStorage.getItem('darkMode') === 'enabled') {
    body.classList.add('dark-mode');
    darkModeToggle.checked = true;
}

darkModeToggle.addEventListener('change', () => {
    if (darkModeToggle.checked) {
        body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'enabled');
    } else {
        body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'disabled');
    }
});

// Close toast messages
document.querySelectorAll('.toast .btn-close').forEach(button => {
    button.addEventListener('click', function() {
        this.closest('.toast').remove();
    });
});

// Auto-remove toasts after 5 seconds
setTimeout(() => {
    document.querySelectorAll('.toast').forEach(toast => {
        toast.remove();
    });
}, 5000);

// Cerrar sidebar al cambiar de tamaño a pantalla grande
window.addEventListener('resize', () => {
    if (window.innerWidth > 992) {
        sidebar.classList.remove('active');
    }
});

// Prevenir scroll del contenido cuando el sidebar está abierto en móviles
menuToggle.addEventListener('click', () => {
    if (sidebar.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
});