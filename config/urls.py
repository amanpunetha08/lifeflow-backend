from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.analytics.views import AnalyticsView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/", include("apps.tasks.urls")),
    path("api/", include("apps.gamification.urls")),
    path("api/", include("apps.scheduler.urls")),
    path("api/analytics/", AnalyticsView.as_view(), name="analytics"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
