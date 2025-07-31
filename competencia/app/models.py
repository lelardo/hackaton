from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

class Closet(models.Model):
    name = models.CharField(max_length=255)

    @classmethod
    def create_with_drawers(cls, name, drawers_data):
        closet = cls.objects.create(name=name)
        
        for drawer_data in drawers_data:
            Drawer.objects.create(
                closet=closet,
                name=drawer_data['name'],
                max_capacity=drawer_data['max_capacity'],
                size=drawer_data['size'],
                type=drawer_data['type']
            )
        
        return closet


class Drawer(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
    ]

    TYPE_CHOICES = [
        ('C', 'Clothes'),
        ('P', 'Papers'),
        ('W', 'Wires'),
    ]
    
    name = models.CharField(max_length=255)
    max_capacity = models.FloatField()
    stored_objects = models.ManyToManyField('Object', blank=True, related_name='drawers_as_list')
    size = models.CharField(
        max_length=1,
        choices=SIZE_CHOICES,
        default='M'
    )
    type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default='C'
    )
    closet = models.ForeignKey(
        Closet,
        on_delete=models.CASCADE,
        related_name='drawers'
    )

    def create_history_record(self, action_type, object_name=None, object_count=None):

        action_messages = {
            'A': 'agregado',
            'D': 'sacado',
            'S': 'ordenado'
        }
        
        action = action_messages.get(action_type)
        if not action:
            raise ValueError("Tipo de acción inválido. Usa 'A' para agregar, 'D' para eliminar, 'S' para ordenar")

        if action_type in ['A', 'D']:
            if object_count and object_count > 1:
                description = f"Se han {action} {object_count} objetos en el cajón {self.name}"
            else:
                description = f"Se ha {action} un objeto {object_name} en el cajón {self.name}"
        else:
            description = f"El cajón {self.name} ha sido {action}"

        History.objects.create(
            description=description,
            date=date.today(),
            drawer=self
        )

    def add_object(self, object):
        if self.stored_objects.count() < self.max_capacity:
            if object.type == self.type:
                self.stored_objects.add(object)
                object.drawer = self
                object.save()
                self.create_history_record('A', object_name=object.name)
            else:
                raise ValidationError("El objeto no es del mismo tipo que el cajón.")
        else:
            raise ValidationError("El cajón ha alcanzado su capacidad máxima.")
    
    def remove_equal_objects(self):
        """
        Elimina objetos duplicados del cajón basándose en nombre, tipo y tamaño.
        Retorna una lista de los objetos que fueron desvinculados.
        """
        objetos = list(self.stored_objects.all())
        vistos = set()
        removed_objects = []

        for obj in objetos:
            clave = (obj.name, obj.type, obj.size)
            if clave in vistos:
                self.stored_objects.remove(obj)
                obj.drawer = None
                obj.save()
                removed_objects.append(obj)
            else:
                vistos.add(clave)

        if removed_objects:
            self.create_history_record('D', object_count=len(removed_objects))

        return removed_objects

    def sort_objects(self):
        self.stored_objects.order_by('size')
        self.save()
        self.create_history_record('S')


class Object(models.Model):
    TYPE_CHOICES = [
        ('C', 'Clothes'),
        ('P', 'Papers'),
        ('W', 'Wires'),
    ]
    
    type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default='C'
    )
    size = models.FloatField(default=1.0)
    name = models.CharField(max_length=255)
    drawer = models.ForeignKey(
        Drawer,
        on_delete=models.CASCADE,
        related_name='drawer_objects'
    )

class History(models.Model):
    description = models.CharField(max_length=255)
    date = models.DateField()
    drawer = models.ForeignKey(
        Drawer,
        on_delete=models.CASCADE,
        related_name='histories'
    )
