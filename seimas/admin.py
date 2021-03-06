from django.contrib import admin
from reversion.admin import VersionAdmin

from seimas.models import Term, Session, Politician, PoliticianDivision, PoliticianParliamentGroup, \
    PoliticianBusinessTrip, PoliticianTerm, PoliticianGame, PoliticianFraction, Fraction, PoliticianCommittee, Committee


class SessionsInline(admin.StackedInline):
    model = Session
    extra = 0


class PoliticianDivisionsInline(admin.StackedInline):
    model = PoliticianDivision
    extra = 0


class PoliticianParliamentGroupsInline(admin.StackedInline):
    model = PoliticianParliamentGroup
    extra = 0


class PoliticianBusinessTripsInline(admin.StackedInline):
    model = PoliticianBusinessTrip
    extra = 0


class PoliticianTermsInline(admin.StackedInline):
    model = PoliticianTerm
    extra = 0


class PoliticianFractionInline(admin.StackedInline):
    model = PoliticianFraction
    extra = 0


class PoliticianCommitteesInline(admin.StackedInline):
    model = PoliticianCommittee
    extra = 0


@admin.register(Term)
class TermAdmin(VersionAdmin):
    search_fields = ['name', 'kad_id']
    list_display = ['name', 'start', 'end', 'kad_id']

    inlines = [
        SessionsInline
    ]


@admin.register(Politician)
class PoliticianAdmin(VersionAdmin):
    search_fields = ['first_name', 'last_name']
    list_display = ['first_name', 'last_name', 'is_active', 'elected_party', 'is_male']
    list_select_related = ['elected_party']
    exclude = ['legal_act_documents']
    list_filter = ['elected_party', 'is_active']

    inlines = [
        PoliticianFractionInline,
        PoliticianCommitteesInline,
        PoliticianTermsInline,
        PoliticianDivisionsInline,
        PoliticianParliamentGroupsInline,
        PoliticianBusinessTripsInline
    ]


@admin.register(Fraction)
class FractionAdmin(VersionAdmin):
    list_display = ['name', 'short_name', 'seimas_pad_id']

    inlines = [
        PoliticianFractionInline
    ]


@admin.register(Committee)
class CommitteeAdmin(VersionAdmin):
    list_display = ['name', 'seimas_pad_id']

    inlines = [
        PoliticianCommitteesInline
    ]


@admin.register(PoliticianGame)
class PoliticianGameAdmin(VersionAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).annotate_with_politicians_answered_count()

    search_fields = ['id']
    date_hierarchy = 'created_at'

    list_display = ['id', 'user', 'email', 'politicians_answered_count', 'time_sec', 'first_politician',
                    'second_politician',
                    'correct_politician', 'lost_on_politician',
                    'user_ip', 'user_agent']
    list_select_related = ['user', 'first_politician', 'second_politician', 'correct_politician', 'lost_on_politician']

    # noinspection PyMethodMayBeStatic
    def time_sec(self, game):
        if game.ended:
            return (game.ended - game.created_at).seconds
        else:
            return "-"

    def politicians_answered_count(self, obj):
        return obj.politicians_answered_count

    politicians_answered_count.admin_order_field = 'politicians_answered_count'
