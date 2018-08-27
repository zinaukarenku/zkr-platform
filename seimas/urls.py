from django.urls import path

from seimas.views import politicians, politician, politician_game

urlpatterns = [
    # path('zaidimas/', politician_game, name="seimas_politician_game"),
    path('politikai/', politicians, name="seimas_politicians"),
    path('politikai/<slug:slug>/', politician, name="seimas_politician")
]
