
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


class ClosetCreateView(APIView):
    def post(self, request):
        try:
            # Validar datos requeridos
            if not request.data.get('name'):
                raise DRFValidationError('El nombre del armario es requerido')
            
            drawers_data = request.data.get('drawers', [])
            if not drawers_data:
                raise DRFValidationError('Se requiere al menos un cajón')

            # Validar datos de cada cajón
            for drawer in drawers_data:
                required_fields = ['name', 'max_capacity', 'size', 'type']
                missing_fields = [field for field in required_fields if field not in drawer]
                if missing_fields:
                    raise DRFValidationError(f'Faltan campos requeridos en el cajón: {", ".join(missing_fields)}')
                
                # Validar que size y type sean valores válidos
                if drawer['size'] not in dict(Drawer.SIZE_CHOICES):
                    raise DRFValidationError(f'Tamaño inválido: {drawer["size"]}. Debe ser S, M o L')
                if drawer['type'] not in dict(Drawer.TYPE_CHOICES):
                    raise DRFValidationError(f'Tipo inválido: {drawer["type"]}. Debe ser C, P o W')
                
                # Validar que max_capacity sea un número positivo
                try:
                    max_capacity = float(drawer['max_capacity'])
                    if max_capacity <= 0:
                        raise DRFValidationError('La capacidad máxima debe ser mayor que 0')
                    drawer['max_capacity'] = max_capacity
                except ValueError:
                    raise DRFValidationError('La capacidad máxima debe ser un número')

            # Crear el armario con sus cajones
            closet = Closet.create_with_drawers(
                name=request.data['name'],
                drawers_data=drawers_data
            )

            # Preparar respuesta
            response_data = {
                'id': closet.id,
                'name': closet.name,
                'drawers': [{
                    'id': drawer.id,
                    'name': drawer.name,
                    'max_capacity': drawer.max_capacity,
                    'size': drawer.size,
                    'type': drawer.type
                } for drawer in closet.drawers.all()]
            }

            return JsonResponse(response_data, status=201)

        except (DRFValidationError, DjangoValidationError) as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)


class ObjectCreateView(APIView):
    def post(self, request):
        try:
            # Validar datos requeridos
            required_fields = ['name', 'type', 'size']
            missing_fields = [field for field in required_fields if field not in request.data]
            if missing_fields:
                raise DRFValidationError(f'Faltan campos requeridos: {", ".join(missing_fields)}')

            # Validar tipo de objeto
            object_type = request.data['type']
            if object_type not in dict(Object.TYPE_CHOICES):
                raise DRFValidationError(f'Tipo inválido: {object_type}. Debe ser C (Clothes), P (Papers) o W (Wires)')

            # Validar tamaño
            try:
                size = float(request.data['size'])
                if size <= 0:
                    raise DRFValidationError('El tamaño debe ser mayor que 0')
            except ValueError:
                raise DRFValidationError('El tamaño debe ser un número')

            # Crear el objeto
            object = Object.objects.create(
                name=request.data['name'],
                type=object_type,
                size=size,
                drawer=None  # El objeto se crea sin asignar a ningún cajón
            )

            # Preparar respuesta
            response_data = {
                'id': object.id,
                'name': object.name,
                'type': object.type,
                'type_display': object.get_type_display(),
                'size': object.size
            }

            return JsonResponse(response_data, status=201)

        except (DRFValidationError, DjangoValidationError) as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)

    
class ObjectAssignView(APIView):
    def post(self, request):
        try:
            # Validar datos requeridos
            required_fields = ['drawer_id', 'object_id']
            missing_fields = [field for field in required_fields if field not in request.data]
            if missing_fields:
                raise DRFValidationError(f'Faltan campos requeridos: {", ".join(missing_fields)}')

            # Obtener el cajón y el objeto
            try:
                drawer = Drawer.objects.get(id=request.data['drawer_id'])
            except Drawer.DoesNotExist:
                raise DRFValidationError(f'No existe un cajón con id {request.data["drawer_id"]}')

            try:
                object = Object.objects.get(id=request.data['object_id'])
            except Object.DoesNotExist:
                raise DRFValidationError(f'No existe un objeto con id {request.data["object_id"]}')

            # Verificar que el objeto no esté ya asignado a un cajón
            if object.drawer is not None:
                raise DRFValidationError(f'El objeto ya está asignado al cajón {object.drawer.name}')

            # Intentar agregar el objeto al cajón
            try:
                drawer.add_object(object)
                drawer.create_history_record('A', object_name=object.name)
            except ValidationError as e:
                raise DRFValidationError(str(e))

            # Preparar respuesta
            response_data = {
                'message': f'Objeto "{object.name}" asignado exitosamente al cajón "{drawer.name}"',
                'drawer': {
                    'id': drawer.id,
                    'name': drawer.name,
                    'type': drawer.type,
                    'current_objects': drawer.stored_objects.count()
                },
                'object': {
                    'id': object.id,
                    'name': object.name,
                    'type': object.type,
                    'size': object.size
                }
            }

            return JsonResponse(response_data, status=200)

        except (DRFValidationError, DjangoValidationError) as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)


class ObjectRemoveFromDrawerView(APIView):
    def post(self, request):
        try:
            # Validar datos requeridos
            if 'object_id' not in request.data:
                raise DRFValidationError('Se requiere el ID del objeto')

            # Obtener el objeto
            try:
                object = Object.objects.get(id=request.data['object_id'])
            except Object.DoesNotExist:
                raise DRFValidationError(f'No existe un objeto con id {request.data["object_id"]}')

            # Verificar que el objeto esté asignado a un cajón
            if object.drawer is None:
                raise DRFValidationError('El objeto no está asignado a ningún cajón')

            # Guardar información antes de desvincular
            drawer_info = {
                'id': object.drawer.id,
                'name': object.drawer.name
            }

            # Desvincular el objeto del cajón
            drawer = object.drawer
            drawer.stored_objects.remove(object)
            object.drawer = None
            object.save()

            # Crear registro histórico
            drawer.create_history_record('D', object_name=object.name)

            # Preparar respuesta
            response_data = {
                'message': f'Objeto "{object.name}" removido exitosamente del cajón "{drawer_info["name"]}"',
                'object': {
                    'id': object.id,
                    'name': object.name,
                    'type': object.type,
                    'size': object.size
                },
                'previous_drawer': drawer_info
            }

            return JsonResponse(response_data, status=200)

        except (DRFValidationError, DjangoValidationError) as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)


class DrawerSortObjectsView(APIView):
    def post(self, request):
        try:
            # Validar datos requeridos
            if 'drawer_id' not in request.data:
                raise DRFValidationError('Se requiere el ID del cajón')

            # Obtener el cajón
            try:
                drawer = Drawer.objects.get(id=request.data['drawer_id'])
            except Drawer.DoesNotExist:
                raise DRFValidationError(f'No existe un cajón con id {request.data["drawer_id"]}')

            # Verificar que el cajón tenga objetos
            if drawer.stored_objects.count() == 0:
                raise DRFValidationError('El cajón está vacío, no hay objetos para ordenar')

            # Ordenar los objetos
            drawer.sort_objects()

            # Obtener la lista ordenada de objetos
            sorted_objects = drawer.stored_objects.order_by('size')
            objects_data = [{
                'id': obj.id,
                'name': obj.name,
                'type': obj.type,
                'type_display': obj.get_type_display(),
                'size': obj.size
            } for obj in sorted_objects]

            # Preparar respuesta
            response_data = {
                'message': f'Objetos del cajón "{drawer.name}" ordenados exitosamente por tamaño',
                'drawer': {
                    'id': drawer.id,
                    'name': drawer.name,
                    'type': drawer.type,
                    'type_display': drawer.get_type_display(),
                    'total_objects': drawer.stored_objects.count()
                },
                'sorted_objects': objects_data
            }

            return JsonResponse(response_data, status=200)

        except (DRFValidationError, DjangoValidationError) as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)


class DrawerRemoveEqualObjectsView(APIView):
    def post(self, request):
        try:
            # Validar datos requeridos
            if 'drawer_id' not in request.data:
                raise DRFValidationError('Se requiere el ID del cajón')

            # Obtener el cajón
            try:
                drawer = Drawer.objects.get(id=request.data['drawer_id'])
            except Drawer.DoesNotExist:
                raise DRFValidationError(f'No existe un cajón con id {request.data["drawer_id"]}')

            # Verificar que el cajón tenga objetos
            if drawer.stored_objects.count() == 0:
                raise DRFValidationError('El cajón está vacío, no hay objetos para revisar')

            # Eliminar objetos duplicados
            removed_objects = drawer.remove_equal_objects()

            # Preparar datos de objetos removidos
            removed_objects_data = [{
                'id': obj.id,
                'name': obj.name,
                'type': obj.type,
                'type_display': obj.get_type_display(),
                'size': obj.size
            } for obj in removed_objects]

            # Preparar datos de objetos que quedaron en el cajón
            remaining_objects = drawer.stored_objects.all()
            remaining_objects_data = [{
                'id': obj.id,
                'name': obj.name,
                'type': obj.type,
                'type_display': obj.get_type_display(),
                'size': obj.size
            } for obj in remaining_objects]

            # Preparar respuesta
            response_data = {
                'message': f'Se han removido {len(removed_objects)} objetos duplicados del cajón "{drawer.name}"',
                'drawer': {
                    'id': drawer.id,
                    'name': drawer.name,
                    'type': drawer.type,
                    'type_display': drawer.get_type_display(),
                    'remaining_objects_count': drawer.stored_objects.count()
                },
                'removed_objects': removed_objects_data,
                'remaining_objects': remaining_objects_data
            }

            return JsonResponse(response_data, status=200)

        except (DRFValidationError, DjangoValidationError) as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)



