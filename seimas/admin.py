from django.contrib import admin
from reversion.admin import VersionAdmin

from seimas.models import Term, Session, Politician, PoliticianDivision, PoliticianParliamentGroup, \
    PoliticianBusinessTrip


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
    list_display = ['first_name', 'last_name', 'is_male', 'elected_party']
    list_select_related = ['elected_party']
    list_filter = ['elected_party']

    inlines = [
        PoliticianDivisionsInline,
        PoliticianParliamentGroupsInline,
        PoliticianBusinessTripsInline
    ]
