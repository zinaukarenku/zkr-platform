from logging import getLogger

from django.contrib import admin
from enumfields.admin import EnumFieldListFilter
from reversion.admin import VersionAdmin

from questions.models import Question, PoliticianAnswer, QuestionStatus
from django.utils.translation import gettext_lazy as _

from utils.utils import try_parse_int

logger = getLogger(__name__)


class QuestionHasAnswer(admin.SimpleListFilter):
    title = _("Klausimo atsakymo būseną")
    parameter_name = 'question_has_answer'

    def lookups(self, request, model_admin):
        return (
            (2, _('Atsakyti klausimai')),
            (3, _('Neatsakyti klausimai')),
        )

    def queryset(self, request, queryset):
        status = try_parse_int(self.value())
        if status == 2:
            return queryset.filter_answered_questions()
        elif status == 3:
            return queryset.exclude_answered_questions()

        return queryset


class PoliticianAnswerInline(admin.StackedInline):
    model = PoliticianAnswer
    raw_id_fields = ['created_by']
    readonly_fields = ['user_ip', 'user_agent', 'user_country']


@admin.register(Question)
class QuestionsAdmin(VersionAdmin):
    search_fields = ['name', 'user_ip', 'politician__name']
    list_display = [
        'question_name',
        'status',
        'is_answered',
        'politician',
        'politician_letter_sent',
        'created_by',
        'created_at',
        'updated_at'
    ]
    list_filter = [
        ('status', EnumFieldListFilter),
        QuestionHasAnswer,
        'is_letter_for_politician_sent',
        'politician__mayor_candidate__municipality__name',
        'created_at'
    ]

    raw_id_fields = ['politician', 'created_by']
    list_select_related = ['politician', 'created_by', 'politian_answer']
    readonly_fields = ['edit_url_for_polician', 'user_ip', 'user_agent', 'user_country']
    view_on_site = True

    date_hierarchy = 'created_at'

    inlines = [
        PoliticianAnswerInline
    ]

    actions = ['send_politician_letters']

    def send_politician_letters(self, request, queryset):
        from questions.tasks import send_new_question_for_politician_letter
        question_ids = list(queryset.values_list('id', flat=True))

        for question_id in question_ids:
            send_new_question_for_politician_letter.delay(question_id=question_id, force_send=True)

        self.message_user(request, f"Netrukus bus išsiųsti ${len(question_ids)} laiškai politikams.")

    send_politician_letters.short_description = _("Persiųsti el. laiškus apie užduotą klausimą politikams")

    def politician_letter_sent(self, obj):
        return obj.is_letter_for_politician_sent

    politician_letter_sent.short_description = _("Laiškas išsiųstas")
    politician_letter_sent.help_text = _(
        "Ar laiškas politikui apie jam užduotą klausimą buvo išsiųstas")
    politician_letter_sent.admin_order_field = 'is_letter_for_politician_sent'
    politician_letter_sent.boolean = True

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
