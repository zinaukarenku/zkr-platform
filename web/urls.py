from django.urls import path
from django.views.generic import RedirectView

from seimas.views import politician_game
from web.views import health_check, subscribe, user_profile

urlpatterns = [
    path('', politician_game, name="seimas_politician_game"),
    path('accounts/profile/', user_profile, name="user_profile"),
    path('accounts/social/connections/', RedirectView.as_view(pattern_name="user_profile", permanent=False)),
    path('health/', health_check, name="health_check"),
    path('subscribe/', subscribe, name="subscribe"),
]