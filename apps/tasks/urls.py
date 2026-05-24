from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TagViewSet

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')
router.register('', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]
