document.addEventListener('DOMContentLoaded', function() {
    // Inicializar todos los toasts
    const toasts = document.querySelectorAll('.toast');
    
    toasts.forEach(toastEl => {
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        });
        toast.show();
        
        // Eliminar el toast del DOM cuando se cierre
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    });
    
    // Control especial para mensajes de intentos fallidos
    const axesMessages = document.querySelectorAll('.toast-body:contains("intentos")');
    if (axesMessages.length > 0) {
        // Retrasar la aparición del mensaje de intentos
        setTimeout(() => {
            axesMessages.forEach(el => {
                const toast = el.closest('.toast');
                if (toast) {
                    const bsToast = bootstrap.Toast.getInstance(toast);
                    if (bsToast) bsToast.show();
                }
            });
        }, 1500); // 1.5 segundos de retraso
    }
});