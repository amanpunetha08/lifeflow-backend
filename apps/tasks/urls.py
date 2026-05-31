from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TagViewSet, HabitsView

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path("tasks/habits/", HabitsView.as_view(), name="habits"),
    path("", include(router.urls)),
]
