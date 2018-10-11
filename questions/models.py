from enum import unique

from django.db import models
from enumfields import EnumIntegerField, Enum

from web.models import PoliticianInfo
from zkr import settings


class Category(models.Model):
    name = models.CharField(max_length=128)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Question categories"

    def __str__(self):
        return self.name


@unique
class QuestionStatus(Enum):
    WAITING_APPROVAL = 1
    REJECTED = 2
    APPROVED = 3

    class Labels:
        WAITING_APPROVAL = 'Waiting approval'
        REJECTED = 'Rejected'
        APPROVED = 'Approved'


class Question(models.Model):
    name = models.CharField(max_length=128, null=True)
    text = models.TextField()

    status = EnumIntegerField(QuestionStatus, db_index=True, default=QuestionStatus.WAITING_APPROVAL)
    rejected_reason = models.TextField(blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, related_name='questions')

    politician = models.ForeignKey(PoliticianInfo, on_delete=models.PROTECT, related_name='questions')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="questions")
    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)

    user_country = models.CharField(max_length=30, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.name or str(self.pk)


class PoliticianAnswer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.PROTECT, related_name='politian_answer')

    text = models.TextField()

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
