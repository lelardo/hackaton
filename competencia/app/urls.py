from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', views.index, name='index'),
    path('recommendation/<int:drawer_id>/', views.RecommendationView.as_view(), name='recommendation'),
    path('objects/create/', ObjectCreateView.as_view(), name='object-create'),
    path('objects/assign/', ObjectAssignView.as_view(), name='object-assign'),
    path('objects/remove-from-drawer/', ObjectRemoveFromDrawerView.as_view(), name='object-remove-from-drawer'),
    path('drawers/sort-objects/', DrawerSortObjectsView.as_view(), name='drawer-sort-objects'),
    path('drawers/remove-duplicates/', DrawerRemoveEqualObjectsView.as_view(), name='drawer-remove-duplicates'),


]
