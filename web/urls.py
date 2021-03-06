from django.urls import path
from django.views.generic import RedirectView

from web.views import health_check, subscribe, user_profile, index, about, join_us

urlpatterns = [
    path('', index, name="index"),
    path('prisijunk/', join_us, name="join_us"),
    path('apie/', about, name="about"),
    path('accounts/profile/', user_profile, name="user_profile"),
    path('health/', health_check, name="health_check"),
    path('subscribe/', subscribe, name="subscribe"),
    path('viktorina/', RedirectView.as_view(url="https://play.kahoot.it/#/k/cd0603d8-b717-432c-bf99-a2f3be7c3b5b")),
    path('viktorina2/', RedirectView.as_view(url="https://play.kahoot.it/#/k/e0d6944f-bed5-4406-80de-fb5791250a52")),
]
