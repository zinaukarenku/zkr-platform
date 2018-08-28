from django.urls import path

from seimas.views import politicians, politician

urlpatterns = [
    path('politikai/', politicians, name="seimas_politicians"),
    path('politikai/<slug:slug>/', politician, name="seimas_politician")
]
