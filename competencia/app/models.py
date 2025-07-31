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
    max_capacity = models.IntegerField()
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

class Object(models.Model):
    identity = models.IntegerField()
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

    
    
