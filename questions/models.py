from enum import unique
from typing import Optional

from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext
from enumfields import EnumIntegerField, Enum

from web.models import PoliticianInfo
from zkr import settings


@unique
class QuestionStatus(Enum):
    WAITING_APPROVAL = 1
    REJECTED = 2
    APPROVED = 3

    class Labels:
        WAITING_APPROVAL = 'Waiting approval'
        REJECTED = 'Rejected'
        APPROVED = 'Approved'


class QuestionsQuerySet(models.QuerySet):
    def filter_questions_by_user(self, user):
        if user and user.is_authenticated:
            return self.filter(created_by=user)

        return self.none()


class ActiveQuestionsManager(models.Manager):
    def get_queryset(self):
        return QuestionsQuerySet(self.model, using=self._db).filter(status=QuestionStatus.APPROVED)


class Question(models.Model):
    name = models.CharField(max_length=128, null=True)
    text = models.TextField()

    status = EnumIntegerField(QuestionStatus, db_index=True, default=QuestionStatus.WAITING_APPROVAL)
    rejected_reason = models.TextField(blank=True, null=True)

    politician = models.ForeignKey(PoliticianInfo, on_delete=models.PROTECT, related_name='questions')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="questions")
    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)

    user_country = models.CharField(max_length=30, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuestionsQuerySet.as_manager()
    active = ActiveQuestionsManager()

    @cached_property
    def politician_photo_url(self) -> Optional[str]:
        politician = self.politician
        if politician.photo:
            return politician.photo.url

    @cached_property
    def last_activity(self):
        if self.has_politician_answer:
            return self.nullable_politician_answer.created_by
        return self.updated_at

    @property
    def politician_name(self):
        return self.politician.name

    @property
    def status_text(self):
        if self.status == QuestionStatus.WAITING_APPROVAL:
            return gettext("Laukia moderatoriaus patvirtinimo")
        if self.status == QuestionStatus.REJECTED:
            return gettext("Klausimas atmestas")
        if self.status == QuestionStatus.APPROVED:
            if self.has_politician_answer:
                return gettext("Klausimas atsakytas")
            return gettext("Klausimas laukia politiko atsakymo")

        raise ValueError(f"Unknown question status: {self.status}")

    @property
    def nullable_politician_answer(self):
        if hasattr(self, 'politian_answer') and self.politian_answer is not None:
            return self.politian_answer
        return None

    @property
    def has_politician_answer(self):
        return self.nullable_politician_answer is not None

    def is_question_for_user(self, user):
        if not user.is_anonymous and self.politician.user == user:
            return True

        return False

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.name or str(self.id)


class PoliticianAnswer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.PROTECT, related_name='politian_answer')

    text = models.TextField(validators=[MinLengthValidator(10)])

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="question_answers")
    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)

    user_country = models.CharField(max_length=30, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Question answers"
