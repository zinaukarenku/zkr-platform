from django.contrib import admin
from reversion.admin import VersionAdmin

from elections.models import Election


@admin.register(Election)
class ElectionAdmin(VersionAdmin):
    search_fields = ['name', 'election_id']
    list_display = ['name', 'slug', 'election_id', 'election_date', 'vr_id', 'vr_id', 'rt_no']
