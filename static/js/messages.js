document.addEventListener('DOMContentLoaded', function() {
    // Configuración base para todos los toasts
    const initToasts = () => {
        const toastElList = document.querySelectorAll('.toast');
        toastElList.forEach(toastEl => {
            // No inicializar toasts que ya están visibles
            if (toastEl.classList.contains('show')) return;
            
            const toast = new bootstrap.Toast(toastEl, {
                autohide: toastEl.dataset.autohide !== 'false',
                delay: toastEl.dataset.delay || 5000
            });
            
            toastEl.addEventListener('hidden.bs.toast', function() {
                toastEl.remove();
            });
            
            toast.show();
        });
    };

    // Inicialización diferida para mensajes importantes
    const initImportantToasts = () => {
        const importantToasts = document.querySelectorAll('.toast[data-delay="8000"]');
        importantToasts.forEach(toastEl => {
            setTimeout(() => {
                const toast = new bootstrap.Toast(toastEl, {
                    autohide: true,
                    delay: 8000
                });
                toast.show();
            }, 500);
        });
    };

    initToasts();
    initImportantToasts();
});