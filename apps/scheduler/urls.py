from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecurringRuleViewSet, ScheduledEventViewSet

router = DefaultRouter()
router.register('rules', RecurringRuleViewSet, basename='recurring-rule')
router.register('events', ScheduledEventViewSet, basename='scheduled-event')

urlpatterns = [
    path('', include(router.urls)),
]
