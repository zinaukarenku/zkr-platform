from django.urls import path

from elections.views import elections, election, president_candidates, president_candidate, mayor_candidate

urlpatterns = [
    path('', elections, name="elections"),
    path('meras/<slug:slug>/', mayor_candidate, name='mayor_candidate'),
    path('prezidentas/', president_candidates, name="president_candidates"),
    path('prezidentas/<slug:slug>/', president_candidate, name="president_candidate"),
    path('<slug:slug>/', election, name="election"),
]
