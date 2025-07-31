from rest_framework import serializers
from .models import Closet, Drawer, Object, History

class ObjectSerializer(serializers.ModelSerializer):
    """
    Serializa los datos del modelo Object.
    """
    # 'type_display' nos da el nombre legible de la opción (ej. 'Clothes')
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Object
        # Incluimos el campo 'drawer' para saber en qué cajón está.
        # 'type_display' es un campo extra para el frontend.
        fields = ['id', 'name', 'type', 'type_display', 'size', 'drawer']
        # Hacemos que 'drawer' sea de solo lectura, ya que lo asignas
        # con una vista de acción específica.
        read_only_fields = ['drawer']



class HistorySerializer(serializers.ModelSerializer):
    """
    Serializa los datos del modelo History.
    """
    class Meta:
        model = History
        fields = ['id', 'description', 'date', 'drawer']



class DrawerSerializer(serializers.ModelSerializer):
    """
    Serializa un Cajón (Drawer) y anida los objetos que contiene.
    """
    # Usamos el ObjectSerializer para mostrar la lista completa de objetos
    # que están dentro del cajón.
    objects = ObjectSerializer(many=True, read_only=True)

    class Meta:
        model = Drawer
        fields = [
            'id',
            'name',
            'max_capacity',
            'size',
            'type',
            'closet',
            'objects'  # Aquí se mostrará la lista de objetos
        ]



class ClosetSerializer(serializers.ModelSerializer):
    """
    Serializa un Armario (Closet) y anida todos sus cajones.
    """
    # Usamos el DrawerSerializer para mostrar la lista de cajones.
    drawers = DrawerSerializer(many=True, read_only=True)

    class Meta:
        model = Closet
        fields = ['id', 'name', 'drawers']



class ClosetCreateSerializer(serializers.ModelSerializer):
    """
    Este serializer es específico para la acción 'create' del ClosetViewSet.
    Define la estructura que se espera recibir para crear un armario y sus cajones.
    """
    # Sobreescribimos el campo 'drawers' para que acepte datos de entrada.
    # Usamos el DrawerSerializer pero solo para escribir (write_only).
    drawers = DrawerSerializer(many=True, write_only=True)

    class Meta:
        model = Closet
        fields = ['id', 'name', 'drawers']

    def create(self, validated_data):
        # Lógica para crear el armario y los cajones a partir de los datos validados.
        drawers_data = validated_data.pop('drawers')
        closet = Closet.objects.create(**validated_data)
        for drawer_data in drawers_data:
            # Quitamos los objetos, ya que no se pueden crear desde aquí
            drawer_data.pop('objects', None) 
            Drawer.objects.create(closet=closet, **drawer_data)
        return closet