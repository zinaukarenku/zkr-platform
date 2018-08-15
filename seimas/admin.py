from django.contrib import admin
from reversion.admin import VersionAdmin

from seimas.models import Term, Session, Politician


class SessionsInline(admin.StackedInline):
    model = Session


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
