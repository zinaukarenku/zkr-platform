from django.contrib import admin
from enumfields.admin import EnumFieldListFilter
from reversion.admin import VersionAdmin

from questions.models import Question, PoliticianAnswer
from django.utils.translation import gettext_lazy as _


class PoliticianAnswerInline(admin.StackedInline):
    model = PoliticianAnswer
    raw_id_fields = ['created_by']
    readonly_fields = ['user_ip', 'user_agent', 'user_country']


@admin.register(Question)
class QuestionsAdmin(VersionAdmin):
    search_fields = ['name', 'user_ip', 'politician__name']
    list_display = ['name', 'status', 'is_answered', 'politician', 'created_by', 'created_at']
    list_filter = [('status', EnumFieldListFilter), ]
    raw_id_fields = ['politician', 'created_by']
    list_select_related = ['politician', 'created_by']
    readonly_fields = ['user_ip', 'user_agent', 'user_country']
    view_on_site = True

    date_hierarchy = 'created_at'

    inlines = [
        PoliticianAnswerInline
    ]

    def is_answered(self, obj):
        return obj.has_politician_answer

    is_answered.short_description = _("Atsakytas")
    is_answered.boolean = True
