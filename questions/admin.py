from django.contrib import admin
from enumfields.admin import EnumFieldListFilter
from reversion.admin import VersionAdmin

from questions.models import Question, Answer, Category


class AnswerInline(admin.StackedInline):
    model = Answer
    raw_id_fields = ['created_by']


@admin.register(Question)
class QuestionsAdmin(VersionAdmin):
    search_fields = ['name', 'user_ip', 'politician__name']
    list_display = ['name', 'status', 'politician', 'category', 'created_by', 'created_at']
    list_filter = [('status', EnumFieldListFilter), 'category']
    autocomplete_fields = ['category']
    raw_id_fields = ['politician', 'created_by']
    list_select_related = ['politician', 'category', 'created_by']

    date_hierarchy = 'created_at'

    inlines = [
        AnswerInline
    ]


@admin.register(Category)
class CategoriesAdmin(VersionAdmin):
    search_fields = ['name']
    list_display = ['name']
