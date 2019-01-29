from django.contrib import admin
from django.utils.html import format_html
from reversion.admin import VersionAdmin

from elections.models import Election, ElectionResult, PresidentCandidate, PresidentCandidateArticle, \
    PresidentCandidateArticleInformation, MayorCandidate
from django.utils.translation import gettext_lazy as _


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


class PresidentCandidateArticleInline(admin.StackedInline):
    model = PresidentCandidateArticle


class PresidentCandidateArticleInformationInline(admin.StackedInline):
    model = PresidentCandidateArticleInformation


@admin.register(PresidentCandidate)
class PresidentCandidateAdmin(VersionAdmin):
    inlines = [PresidentCandidateArticleInline]
    search_fields = ['name']
    list_display = ['name', 'photo', 'candidate_program', 'created_at', 'updated_at']
    exclude = ['slug']
    view_on_site = True


@admin.register(MayorCandidate)
class MayorCandidateAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'party', 'municipality']
    list_display = ['first_name', 'last_name', 'party', 'municipality', 'created_at', 'updated_at']
    list_filter = ['municipality', 'party']
    exclude = ['slug']


@admin.register(PresidentCandidateArticle)
class PresidentCandidateArticleAdmin(VersionAdmin):
    search_fields = ['candidate__name', 'url']
    list_display = ['candidate', 'article_url', 'created_at']
    list_select_related = ['candidate']
    list_filter = ['candidate__name', ]
    inlines = [PresidentCandidateArticleInformationInline]

    def article_url(self, obj):
        return format_html('<a href="{url}" target="_blank">{url}</a>', url=obj.url)

    article_url.short_description = _("Naujienos nuoroda")
