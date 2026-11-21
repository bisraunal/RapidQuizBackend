from django.contrib import admin
from django.urls import path, include
from quiz_api.views import ApiRootView, HealthCheckView

urlpatterns = [
    path('', ApiRootView.as_view(), name='root'),
    path('health/', HealthCheckView.as_view(), name='root-health'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('quiz_api.urls')),
]
