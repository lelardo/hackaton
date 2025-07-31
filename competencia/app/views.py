import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Closet, Drawer, Object, History
from .serializers import (
    ClosetSerializer,
    DrawerSerializer,
    ObjectSerializer,
    HistorySerializer,
    ClosetCreateSerializer
)

class ClosetViewSet(viewsets.ModelViewSet):
    """
    API para gestionar Armarios (Closets).
    """
    queryset = Closet.objects.all().order_by('id')

    def get_serializer_class(self):
        # Usa un serializer para crear y otro para mostrar.
        if self.action == 'create':
            return ClosetCreateSerializer
        return ClosetSerializer

class DrawerViewSet(viewsets.ModelViewSet):
    """
    API para gestionar Cajones (Drawers) y sus acciones.
    """
    queryset = Drawer.objects.all().order_by('id')
    serializer_class = DrawerSerializer

    def get_queryset(self):
        queryset = Drawer.objects.all().order_by('id')
        closet_id = self.request.query_params.get('closet', None)
        if closet_id is not None:
            queryset = queryset.filter(closet_id=closet_id)
        return queryset

    @action(detail=True, methods=['post'], url_path='assign-object')
    def assign_object(self, request, pk=None):
        """
        Asigna un objeto a este cajón.
        Espera en el body: { "object_id": ID_DEL_OBJETO }
        """
        drawer = self.get_object()
        object_id = request.data.get('object_id')
        if not object_id:
            return Response({'error': 'Se requiere el ID del objeto (object_id)'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = Object.objects.get(id=object_id)
            if obj.drawer:
                return Response({'error': 'El objeto ya esta asignado a otro cajon'}, status=status.HTTP_400_BAD_REQUEST)

            drawer.add_object(obj)
            drawer.create_history_record('A', object_name=obj.name)
            
            # Devuelve el cajón actualizado
            serializer = self.get_serializer(drawer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Object.DoesNotExist:
            return Response({'error': 'Objeto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='recommendation')
    def recommendation(self, request, pk=None):
        """
        Obtiene una recomendación de la IA para este cajón.
        """
        drawer = self.get_object()
        objects = drawer.objects.all()
        
        # (Aquí va la misma lógica para llamar a Gemini que ya tenías)
        # prompt = self.build_prompt(drawer, objects)
        # ... llamada a requests ...
        recommendation_text = "Esta es tu recomendacion de prueba para el cajon " + drawer.name
        
        return Response({'recommendation': recommendation_text})

    # Puedes añadir aquí las otras acciones: remove-object, sort-objects, etc.

class ObjectViewSet(viewsets.ModelViewSet):
    """
    API para gestionar Objetos (Objects).
    """
    queryset = Object.objects.all().order_by('id')
    serializer_class = ObjectSerializer

class HistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API de solo lectura para ver el historial.
    """
    queryset = History.objects.all().order_by('-date')
    serializer_class = HistorySerializer