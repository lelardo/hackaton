
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from http import HTTPStatus
from django.http import Http404
import os
import requests
from django.http import JsonResponse
from django.views import View
from .models import Drawer, Object

# class Class_Ejemplo(APIView):
    
    
#     def get(self, request):
#         #return HttpResponse(f"Método GET | id={request.GET.get('id', None)} | slug={request.GET.get('slug')}")
#         #return Response({"estado":"ok", "mensaje":f"Método GET | id={request.GET.get('id', None)} | slug={request.GET.get('slug')}"})
#         return JsonResponse({"estado":"ok", "mensaje":f"Método GET | id={request.GET.get('id', None)} | slug={request.GET.get('slug')}"}, status=HTTPStatus.OK)
    
    
#     def post(self, request):
#         if request.data.get("correo")==None or request.data.get("password")==None:
#             raise Http404
#         #return HttpResponse("Método POST")
#         return JsonResponse({"estado":"ok", "mensaje":f"Método POST | correo={request.data.get('correo')} | password={request.data.get('password')}"}, status=HTTPStatus.CREATED)
    

# class Class_EjemploParametros(APIView):
    
    
#     def get(self, request, id):
#         return HttpResponse(f"Método GET | parámetro={id}")
    
    
#     def put(self, request, id):
#         return HttpResponse(f"Método PUT | parámetro={id}")
    
    
#     def delete(self, request, id):
#         return HttpResponse(f"Método DELETE | parámetro={id}")


# class Class_EjemploUpload(APIView):
    
    
#     def post(self, request):
#         fs = FileSystemStorage()
#         fecha = datetime.now()
#         foto = f"{datetime.timestamp(fecha)}{os.path.splitext(str(request.FILES['file']))[1]}"
#         fs.save(f"ejemplo/{foto}", request.FILES['file'])
#         fs.url( request.FILES['file'])
#         return JsonResponse({"estado":"ok", "mensaje":"Se subió el archivo"})
    
class RecommendationView(View):
    def get(self, request, drawer_id):
        try:
            drawer = Drawer.objects.get(id=drawer_id)
            objects = Object.objects.filter(drawer=drawer)
            
            # Construye el prompt para la API de Gemini
            prompt = self.build_prompt(drawer, objects)
            
            # Llama a la API de Gemini usando la clave desde settings
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
            
            response.raise_for_status() # Lanza un error si la API devuelve un código de error (4xx o 5xx)
            
            # Procesa la respuesta de la API
            # La recomendación de texto está dentro de la estructura JSON de la respuesta
            gemini_response = response.json()
            recommendation_text = gemini_response['candidates'][0]['content']['parts'][0]['text']

            # Puedes guardar la recomendación en un modelo History si lo tienes
            # History.objects.create(drawer=drawer, recommendation=recommendation_text)
            
            return JsonResponse({"recommendation": recommendation_text})

        except Drawer.DoesNotExist:
            return JsonResponse({"error": "El cajón no existe"}, status=404)
        except requests.exceptions.RequestException as e:
            # Captura errores específicos de la llamada a la API
            return JsonResponse({"error": f"Error al contactar la API de Gemini: {e}"}, status=500)
        except Exception as e:
            # Captura cualquier otro error
            return JsonResponse({"error": f"Ha ocurrido un error inesperado: {str(e)}"}, status=500)

    def build_prompt(self, drawer, objects):
        # Información del cajón
        drawer_info = f"El cajón '{drawer.name}' tiene una capacidad máxima de {drawer.max_capacity} objetos, es de tamaño '{drawer.get_size_display()}' y de tipo '{drawer.get_type_display()}'."
        
        # Información de los objetos
        object_list = ", ".join([obj.name for obj in objects])
        objects_info = f"Actualmente contiene {objects.count()} objetos: {object_list}."
        
        # Reglas de recomendación
        rules = """
        Eres un asistente experto en organización de espacios. Analiza la siguiente información sobre un cajón y su contenido. 
        Luego, genera una recomendación clara y útil para el usuario, en español, basándote en las siguientes reglas:

        1. Regla de Capacidad: Si el cajón supera el 80% de su capacidad, sugiere mover algunos objetos a otro cajón del mismo tipo con más espacio o considera la posibilidad de obtener un nuevo cajón.
        2. Regla de Tipo de Objeto: Si el cajón contiene objetos que no coinciden con su tipo (ej: calcetines en un cajón de documentos), recomienda moverlos al cajón correcto.
        3. Regla de Espacio no Utilizado: Si el cajón está por debajo del 20% de su capacidad, sugiere consolidar su contenido en otro cajón del mismo tipo para liberar espacio.

        Proporciona una respuesta amigable y directa al usuario.
        """
        
        return f"{drawer_info} {objects_info}\n\n{rules}"