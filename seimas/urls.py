from django.urls import path

from seimas.views import politicians, politician, politician_game, index

urlpatterns = [
    path('', index, name="seimas_index"),
    path('nariai/', politicians, name="seimas_politicians"),
    path('nariai/<int:page>/', politicians, name="seimas_politicians"),
    path('nariai/<slug:slug>/', politician, name="seimas_politician"),
    path('zaidimas/', politician_game, name="seimas_politician_game"),
]
