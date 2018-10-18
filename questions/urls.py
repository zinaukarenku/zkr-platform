from django.urls import path

from questions.views import questions_list, new_question, question

urlpatterns = [
    path('', questions_list, name="questions_list"),
    path('klausimas/', new_question, name="new_question"),
    path('klausimas/<int:question_id>/', question, name="question"),

]
