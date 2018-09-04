from django.urls import path
from django.views.generic import RedirectView

from web.views import health_check, subscribe, user_profile, index, about, join_us

urlpatterns = [
    path('', index, name="index"),
    path('prisijunk/', join_us, name="join_us"),
    path('apie/', about, name="about"),
    path('accounts/profile/', user_profile, name="user_profile"),
    path('accounts/social/connections/', RedirectView.as_view(pattern_name="user_profile", permanent=False)),
    path('health/', health_check, name="health_check"),
    path('subscribe/', subscribe, name="subscribe"),
]
