from enum import unique
from typing import Optional
from urllib.parse import urljoin

import reversion
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.functional import cached_property
from enumfields import EnumIntegerField, Enum
from django.utils.translation import gettext_lazy as _

from web.models import PoliticianInfo
from zkr import settings


@unique
class QuestionStatus(Enum):
    WAITING_APPROVAL = 1
    REJECTED = 2
    APPROVED = 3

    class Labels:
        WAITING_APPROVAL = _('Laukia patvirtinimo')
        REJECTED = _('Atmestas')
        APPROVED = _("Pavirtintas")


class QuestionsQuerySet(models.QuerySet):
    def filter_questions_by_user(self, user):
        if user and user.is_authenticated:
            return self.filter(created_by=user)

        return self.none()

    def filter_questions_by_user_or_for_user(self, user):
        if user and user.is_authenticated:
            return self.filter(
                Q(created_by=user) | Q(politician__authenticated_users=user, status=QuestionStatus.APPROVED)
            )

        return self.none()


class ActiveQuestionsManager(models.Manager):
    def get_queryset(self):
        return QuestionsQuerySet(self.model, using=self._db).filter(status=QuestionStatus.APPROVED)


@reversion.register()
class Question(models.Model):
    name = models.CharField(max_length=128, null=True, verbose_name=_("Klausimo pavadinimas"))
    text = models.TextField(validators=[MinLengthValidator(15), MaxLengthValidator(500)],
                            verbose_name=_("Klausimo tekstas"))

    status = EnumIntegerField(QuestionStatus, db_index=True, default=QuestionStatus.WAITING_APPROVAL,
                              verbose_name=_("Klausimo būsena"))
    rejected_reason = models.TextField(blank=True, null=True, verbose_name=_("Klausimo atmetimo priežastis"),
                                       help_text=_("Būtina užpildyti jei klausimas yra atmetamas"))

    politician = models.ForeignKey(PoliticianInfo, on_delete=models.PROTECT, related_name='questions',
                                   verbose_name=_("Politikas"),
                                   help_text=_("Nurodo politiką, kuriam skirtas klausimas"))

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="questions",
                                   verbose_name=_("Klausimo autorius"))
    user_ip = models.GenericIPAddressField(verbose_name=_("Klausimo autoriaus IP"), blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True, verbose_name=_("Klausimo autoriaus User-agent"))

    user_country = models.CharField(max_length=30, blank=True, null=True,
                                    verbose_name=_("Klausimo autoriaus šalis"))

    is_moderator_decision_letter_sent = models.BooleanField(
        default=False,
        verbose_name=_("Ar išsiųstas laiškas apie klausimo patvirtnimą / atmetimą")
    )

    is_letter_for_politician_sent = models.BooleanField(
        default=False,
        verbose_name=_("Ar laiškas politikui apie jam užduotą klausimą buvo išsiųstas")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Klausimas sukūrimo data"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Klausimo atnaujinimo data"))

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
            return self.nullable_politician_answer.created_at
        return self.updated_at

    @property
    def politician_name(self):
        return self.politician.name

    @property
    def status_text(self):
        if self.status == QuestionStatus.WAITING_APPROVAL:
            return _("Laukia moderatoriaus patvirtinimo")
        if self.status == QuestionStatus.REJECTED:
            return _("Klausimas atmestas")
        if self.status == QuestionStatus.APPROVED:
            if self.has_politician_answer:
                return _("Klausimas atsakytas")
            return _("Klausimas laukia politiko atsakymo")

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
        if not user.is_anonymous and user in self.politician.authenticated_users.all():
            return True

        return False

    @property
    def question_author_email(self) -> str:
        return self.created_by.email

    def get_absolute_url(self):
        return urljoin(settings.BASE_DOMAIN, reverse("question", kwargs={'question_id': self.id}))

    def get_editable_absolute_url_for_politician(self):
        return urljoin(settings.BASE_DOMAIN, reverse("question",
                                                     kwargs={
                                                         'question_id': self.id,
                                                         'secret_id': self.politician.registration_secret_id
                                                     }))

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = _("Klausimai politikams")
        verbose_name = _("Klausimas politikui")

    def __str__(self):
        return self.name or str(self.id)


@reversion.register()
class PoliticianAnswer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.PROTECT, related_name='politian_answer')

    text = models.TextField(validators=[MinLengthValidator(10)], verbose_name=_("Politiko atsakymas"))

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="question_answers", verbose_name=_("Atsakymo autorius"))
    user_ip = models.GenericIPAddressField(verbose_name=_("Atsakymo autoriaus IP"), blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True, verbose_name=_("Atsakymo autoriaus User-agent"))

    user_country = models.CharField(max_length=30, blank=True, null=True,
                                    verbose_name=_("Atsakymo autoriaus šalis"))

    is_question_answered_letter_sent = models.BooleanField(
        default=False,
        verbose_name=_("Ar laiškas apie atsakytą klausimą buvo išsiųstas")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = _("Politikų atsakymai")
        verbose_name = _("Politiko atsakymas")
