from django.contrib import admin
from reversion.admin import VersionAdmin

from seimas.models import Term, Session, Politician, PoliticianDivision, PoliticianParliamentGroup, \
    PoliticianBusinessTrip, PoliticianTerm


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
    list_filter = ['elected_party', 'is_active']

    inlines = [
        PoliticianTermsInline,
        PoliticianDivisionsInline,
        PoliticianParliamentGroupsInline,
        PoliticianBusinessTripsInline,
    ]
