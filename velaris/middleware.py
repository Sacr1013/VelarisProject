from django.contrib import messages
from axes.handlers.proxy import AxesProxyHandler
from django.shortcuts import redirect

class AuthMessageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if hasattr(response, 'render') and callable(response.render):
            return self.process_template_response(request, response)
        return response

    def process_template_response(self, request, response):
        # Limpiar mensajes duplicados de Axes
        storage = messages.get_messages(request)
        axes_messages = [msg for msg in storage if 'axes' in msg.extra_tags]
        storage.used = True  # Marcar todos como leídos
        
        # Si hay mensajes de Axes, agregar uno limpio
        if axes_messages:
            messages.error(request, 
                         "Demasiados intentos fallidos. Cuenta bloqueada temporalmente.", 
                         extra_tags='auth axes-lockout')
        
        return response
    
class AdminURLAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Bloquear acceso a URLs que contengan '/admin' o '/management'
        if not request.user.is_staff and any(
            path in request.path for path in ['/admin', '/management']
        ):
            return redirect('home')
            
        return response