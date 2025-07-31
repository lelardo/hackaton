from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClosetViewSet, DrawerViewSet, ObjectViewSet, HistoryViewSet


router = DefaultRouter()


router.register(r'closets', ClosetViewSet, basename='closet')
router.register(r'drawers', DrawerViewSet, basename='drawer')
router.register(r'objects', ObjectViewSet, basename='object')
router.register(r'history', HistoryViewSet, basename='history')

urlpatterns = [
    path('', include(router.urls)),
]