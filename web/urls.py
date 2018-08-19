from django.urls import path

from web.views import health_check, subscribe, index

urlpatterns = [
    path('', index, name="index"),
    path('health/', health_check, name="health_check"),
    path('subscribe/', subscribe, name="subscribe"),
]
