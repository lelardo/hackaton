from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    #path('ejemplo', views.Class_Ejemplo.as_view()),
    #path('ejemplo/<int:id>', views.Class_EjemploParametros.as_view()),
    #path('ejemplo-upload', views.Class_EjemploUpload.as_view()),

]
