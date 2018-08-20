from django.urls import path
from django.views.generic import RedirectView

from web.views import health_check, subscribe, index, user_profile

urlpatterns = [
    path('', index, name="index"),
    path('accounts/profile/', user_profile, name="user_profile"),
    path('accounts/social/connections/', RedirectView.as_view(pattern_name="user_profile", permanent=False)),
    path('health/', health_check, name="health_check"),
    path('subscribe/', subscribe, name="subscribe"),
]
