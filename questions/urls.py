from django.urls import path

from questions.views import index, new_question

urlpatterns = [
    path('', index, name="questions_index"),
    path('klausimas/', new_question, name="new_question"),
]
