from django.contrib import admin
from reversion.admin import VersionAdmin

from elections.models import Election, ElectionResult


@admin.register(Election)
class ElectionAdmin(VersionAdmin):
    search_fields = ['name', 'election_id']
    list_display = ['name', 'is_active', 'slug', 'election_id', 'election_date', 'last_results_update', 'vr_id',
                    'vr_id', 'rt_no']


@admin.register(ElectionResult)
class ElectionAdmin(VersionAdmin):
    search_fields = ['name']
    list_select_related = ['election']
    list_filter = ['election']
    list_display = ['name', 'party', 'photo', 'election', 'candidate_id', 'postal_votes', 'ballot_votes',
                    'percent_ballot_paper', 'percent_voters', 'created_at', 'updated_at']
