from enum import unique
from typing import Optional

from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.urls import reverse
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
        WAITING_APPROVAL = gettext('Laukia patvirtinimo')
        REJECTED = gettext('Atmestas')
        APPROVED = gettext("Pavirtintas")


class QuestionsQuerySet(models.QuerySet):
    def filter_questions_by_user(self, user):
        if user and user.is_authenticated:
            return self.filter(created_by=user)

        return self.none()


class ActiveQuestionsManager(models.Manager):
    def get_queryset(self):
        return QuestionsQuerySet(self.model, using=self._db).filter(status=QuestionStatus.APPROVED)


class Question(models.Model):
    name = models.CharField(max_length=128, null=True, verbose_name=gettext("Klausimo pavadinimas"))
    text = models.TextField(validators=[MinLengthValidator(30), MaxLengthValidator(2000)],
                            verbose_name=gettext("Klausimo tekstas"))

    status = EnumIntegerField(QuestionStatus, db_index=True, default=QuestionStatus.WAITING_APPROVAL,
                              verbose_name=gettext("Klausimo būsena"))
    rejected_reason = models.TextField(blank=True, null=True, verbose_name=gettext("Klausimo atmetimo priežastis"),
                                       help_text=gettext("Būtina užpildyti jei klausimas yra atmetamas"))

    politician = models.ForeignKey(PoliticianInfo, on_delete=models.PROTECT, related_name='questions',
                                   verbose_name=gettext("Politikas"),
                                   help_text=gettext("Nurodo politiką, kuriam skirtas klausimas"))

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="questions",
                                   verbose_name=gettext("Klausimo autorius"))
    user_ip = models.GenericIPAddressField(verbose_name=gettext("Klausimo autoriaus IP"))
    user_agent = models.TextField(blank=True, null=True, verbose_name=gettext("Klausimo autoriaus User-agent"))

    user_country = models.CharField(max_length=30, blank=True, null=True,
                                    verbose_name=gettext("Klausimo autoriaus šalis"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=gettext("Klausimas sukūrimo data"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=gettext("Klausimo atnaujinimo data"))

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

    def get_absolute_url(self):
        return reverse("question", kwargs={'question_id': self.id})

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = gettext("Klausimai politikams")
        verbose_name = gettext("Klausimas politikui")

    def __str__(self):
        return self.name or str(self.id)


class PoliticianAnswer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.PROTECT, related_name='politian_answer')

    text = models.TextField(validators=[MinLengthValidator(10)], verbose_name=gettext("Politiko atsakymas"))

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="question_answers", verbose_name=gettext("Atsakymo autorius"))
    user_ip = models.GenericIPAddressField(verbose_name=gettext("Atsakymo autoriaus IP"))
    user_agent = models.TextField(blank=True, null=True, verbose_name=gettext("Atsakymo autoriaus User-agent"))

    user_country = models.CharField(max_length=30, blank=True, null=True,
                                    verbose_name=gettext("Atsakymo autoriaus šalis"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = gettext("Politikų atsakymai")
        verbose_name = gettext("Politiko atsakymas")
