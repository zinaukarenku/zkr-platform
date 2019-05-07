from django.urls import path

from elections.views import elections, election, president_candidates, president_candidate, mayor_candidates, \
    mayor_candidate, debates, ep_candidates, ep_candidate

urlpatterns = [
    path('', elections, name="elections"),
    path('debatai/', debates, name="debates"),
    path('kandidatai-i-merus/', mayor_candidates, name='mayor_candidates'),
    path('kandidatai-i-merus/<int:page>/', mayor_candidates, name='mayor_candidates'),
    path('kandidatai-i-merus/<slug:slug>/', mayor_candidate, name='mayor_candidate'),
    path('kandidatai-i-prezidentus/', president_candidates, name="president_candidates"),
    path('prezidentas/<slug:slug>/', president_candidate, name="president_candidate"),
    path('kandidatai-i-euro-parlamenta/', ep_candidates, name="ep_candidates"),
    path('kandidatai-i-euor-parlamenta/', ep_candidate, name="ep_candidate"),
    path('<slug:slug>/', election, name="election"),
]
