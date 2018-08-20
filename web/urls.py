from django.urls import path

from web.views import health_check, subscribe, index, user_profile

urlpatterns = [
    path('', index, name="index"),
    path('accounts/profile/', user_profile, name="user_profile"),
    path('health/', health_check, name="health_check"),
    path('subscribe/', subscribe, name="subscribe"),
]
