from django.db import models

class Closet(models.Model):
    name = models.CharField(max_length=255)



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
    objects = models.ManyToManyField('Object', blank=True, related_name='drawers_as_list')
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

    def add_object(self, object):
        if self.objects.count() < self.max_capacity:
            self.objects.add(object)
            object.drawer = self
            object.save()
        else:
            raise ValidationError("El cajón ha alcanzado su capacidad máxima.")

    def sort_objects(self):
        self.objects.order_by('size')
        self.save()


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
    size = models.FloatField()
    name = models.CharField(max_length=255)
    drawer = models.ForeignKey(
        Drawer,
        on_delete=models.CASCADE,
        related_name='objects'
    )

class History(models.Model):
    description = models.CharField(max_length=255)
    date = models.DateField()
    drawer = models.ForeignKey(
        Drawer,
        on_delete=models.CASCADE,
        related_name='histories'
    )

    def create_register(self, type, object_name=None, objecto_count=None):
        types = {
            'D': 'borrado',
            'O': 'ordenado',
            'A': 'agregado',
        }
        if type == 'D' or type == 'A':
            if objecto_count > 1:
                self.description = f"Se ha {type} {objecto_count} objetos {object_name} en el cajón {self.drawer.name}"
            else:
                self.description = f"Se ha {type} un objeto {object_name} en el cajón {self.drawer.name}"
        else:
            self.description = f"Se ha {type} el cajón {self.drawer.name}"
        
        self.save()

    
    

