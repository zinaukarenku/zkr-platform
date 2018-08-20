from django.urls import path, include

from web.views import health_check, subscribe, index

urlpatterns = [
    path('', index, name="index"),
    path('health/', health_check, name="health_check"),
    path('subscribe/', subscribe, name="subscribe"),
    path('accounts/', include('allauth.urls')),
]
