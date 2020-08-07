from django.urls import path

from elections.views import elections, election, elections_2019, president_candidates, president_candidate, \
    mayor_candidates, \
    mayor_candidate, debates_2019, ep_candidates, ep_candidate, debates_2020, seimas_candidate, seimas_candidates

urlpatterns = [
    path('', elections, name="elections"),
    path('2019/', elections_2019, name="elections_2019"),

    path('debatai/', debates_2020, name="debates"),
    path('debatai-2019/', debates_2019, name="debates_2019"),

    path('kandidatai-i-seima/', seimas_candidates, name='seimas_candidates'),
    path('kandidatai-i-seima/<int:page>/', seimas_candidates, name='seimas_candidates'),
    path('kandidatai-i-seima/<slug:slug>/', seimas_candidate, name='seimas_candidate'),

    path('kandidatai-i-merus/', mayor_candidates, name='mayor_candidates'),
    path('kandidatai-i-merus/<int:page>/', mayor_candidates, name='mayor_candidates'),
    path('kandidatai-i-merus/<slug:slug>/', mayor_candidate, name='mayor_candidate'),

    path('kandidatai-i-prezidentus/', president_candidates, name="president_candidates"),
    path('prezidentas/<slug:slug>/', president_candidate, name="president_candidate"),
    path('kandidatai-i-euro-parlamenta/', ep_candidates, name="ep_candidates"),
    path('kandidatai-i-euor-parlamenta/', ep_candidate, name="ep_candidate"),
    path('<slug:slug>/', election, name="election"),
]
