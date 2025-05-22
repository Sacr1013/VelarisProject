from django.contrib import messages
from axes.handlers.proxy import AxesProxyHandler

class AuthMessageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Solo procesar para respuestas que renderizan templates
        if hasattr(response, 'render') and callable(response.render):
            return self.process_template_response(request, response)
        return response

    def process_template_response(self, request, response):
        if hasattr(request, 'axes_locked_out'):
            # Limpiar mensajes previos de axes
            storage = messages.get_messages(request)
            for message in storage:
                if 'axes' not in message.extra_tags:
                    storage.used = False
            
            # Añadir mensaje personalizado
            messages.error(request, 
                         "Demasiados intentos fallidos. Cuenta bloqueada temporalmente.", 
                         extra_tags='axes auth')
        
        return response