from django.urls import path
from django.views.generic import RedirectView

from questions.views import questions_list, after_registration_list, new_question, question, question_with_secret

urlpatterns = [
    path('', questions_list, name="questions_list"),
    path('auth/<uuid:secret_id>/', after_registration_list, name="questions_list_after_registration"),
    path('<int:page>/', questions_list, name="questions_list"),
    path('klausimas/naujas/', new_question, name="new_question"),
    path('klausimas/naujas/<int:politician_id>/', new_question, name="new_question"),
    path('klausimas/<int:question_id>/', question, name="question"),
    path('klausimas/<int:question_id>/auth/<uuid:secret_id>/', question_with_secret, name="question"),
    path('klausimas/', RedirectView.as_view(pattern_name="new_question", permanent=False))
]
