from django.contrib import admin
from .models import Closet, Drawer, Object , History 

# Register your models here.
admin.site.register(Closet)
admin.site.register(Drawer)
admin.site.register(Object)
admin.site.register(History)
