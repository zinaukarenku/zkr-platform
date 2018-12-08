from django.urls import path

from elections.views import election, president_candidates, president_candidate

urlpatterns = [
    path('prezidentas/', president_candidates, name="president_candidates"),
    path('prezidentas/<slug:slug>/', president_candidate, name="president_candidate"),
    path('<slug:slug>/', election, name="election"),
]
