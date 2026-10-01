from django.contrib import admin
from django.urls import path, include
from quiz_api.views import ApiRootView

urlpatterns = [
    path('', ApiRootView.as_view(), name='root'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('quiz_api.urls')),
]
