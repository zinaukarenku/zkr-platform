from logging import getLogger

from django.contrib import admin
from enumfields.admin import EnumFieldListFilter
from reversion.admin import VersionAdmin

from questions.models import Question, PoliticianAnswer, QuestionStatus
from django.utils.translation import gettext_lazy as _

logger = getLogger(__name__)


class PoliticianAnswerInline(admin.StackedInline):
    model = PoliticianAnswer
    raw_id_fields = ['created_by']
    readonly_fields = ['user_ip', 'user_agent', 'user_country']


@admin.register(Question)
class QuestionsAdmin(VersionAdmin):
    search_fields = ['name', 'user_ip', 'politician__name']
    list_display = ['question_name', 'status', 'is_answered', 'politician', 'created_by', 'created_at']
    list_filter = [('status', EnumFieldListFilter), ]
    raw_id_fields = ['politician', 'created_by']
    list_select_related = ['politician', 'created_by']
    readonly_fields = ['edit_url_for_polician', 'user_ip', 'user_agent', 'user_country']
    view_on_site = True

    date_hierarchy = 'created_at'

    inlines = [
        PoliticianAnswerInline
    ]

    def edit_url_for_polician(self, obj):
        return obj.get_editable_absolute_url_for_politician()

    edit_url_for_polician.short_description = _("Klausimo atsakymo nuoroda politikui")
    edit_url_for_polician.help_text = _(
        "Nuoroda, kurią paspaudes užsiregistravęs politikas galės atsakyti į jam užduotus klausimus. "
        "Šią nuorodą galima duoti tik politikams ir negalima platinti viešai!!!")

    def question_name(self, obj):
        if obj.name:
            return obj.name

        if obj.status == QuestionStatus.WAITING_APPROVAL:
            return _('Laukia patvirtinimo')

        if obj.status == QuestionStatus.REJECTED:
            return _('Atmestas')

        logger.warning("Unable to output question name", exc_info=True)
        return ""

    question_name.short_description = _("Klausimo pavadinimas")

    def is_answered(self, obj):
        return obj.has_politician_answer

    is_answered.short_description = _("Atsakytas")
    is_answered.boolean = True
