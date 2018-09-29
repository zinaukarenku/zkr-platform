from django.urls import path

from elections.views import election

urlpatterns = [
    path('<slug:slug>/', election, name="election"),
]
