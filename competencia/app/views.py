
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views import View  
from .models import Drawer, Object

def index(request):
    from django.http import HttpResponse
    return HttpResponse("Página principal de la app.")

class RecommendationView(View): 
    def get(self, request, drawer_id):
        try:
            drawer = Drawer.objects.get(id=drawer_id)
            objects = Object.objects.filter(drawer=drawer)
            
            prompt = self.build_prompt(drawer, objects)
            
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                return JsonResponse({"error": "La clave GEMINI_API_KEY no está configurada en tu archivo .env"}, status=500)

            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                headers={
                    'Content-Type': 'application/json',
                    'x-goog-api-key': api_key
                },
                json={"contents": [{"parts": [{"text": prompt}]}]}
            )
            
            response.raise_for_status()
            
            gemini_response = response.json()
            recommendation_text = gemini_response['candidates'][0]['content']['parts'][0]['text']

            return JsonResponse({"recommendation": recommendation_text})

        except Drawer.DoesNotExist:
            return JsonResponse({"error": f"El cajón con id={drawer_id} no existe"}, status=404)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Error al contactar la API de Gemini: {e}"}, status=500)
        except Exception as e:
            return JsonResponse({"error": f"Ha ocurrido un error inesperado: {str(e)}"}, status=500)

    def build_prompt(self, drawer, objects):
       
        drawer_info = f"El cajón '{drawer.name}' tiene una capacidad máxima de {drawer.max_capacity} objetos, es de tamaño '{drawer.get_size_display()}' y de tipo '{drawer.get_type_display()}'."
        object_list = ", ".join([obj.name for obj in objects])
        objects_info = f"Actualmente contiene {objects.count()} objetos: {object_list}."
        rules = """
        Eres un asistente experto en organización de espacios. Analiza la siguiente información sobre un cajón y su contenido. 
        Luego, genera una recomendación clara y útil para el usuario, en español, basándote en las siguientes reglas:

        1. Regla de Capacidad: Si el cajón supera el 80% de su capacidad, sugiere mover algunos objetos a otro cajón del mismo tipo con más espacio o considera la posibilidad de obtener un nuevo cajón.
        2. Regla de Tipo de Objeto: Si el cajón contiene objetos que no coinciden con su tipo (ej: calcetines en un cajón de documentos), recomienda moverlos al cajón correcto.
        3. Regla de Espacio no Utilizado: Si el cajón está por debajo del 20% de su capacidad, sugiere consolidar su contenido en otro cajón del mismo tipo para liberar espacio.

        Proporciona una respuesta amigable , no uses tildes ni acentos y directa al usuario. Usa palabras más naturales y se más concreto en el mensaje.
        """
        return f"{drawer_info} {objects_info}\n\n{rules}"