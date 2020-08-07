from django.contrib import admin
from django.utils.html import format_html
from reversion.admin import VersionAdmin

from elections.models import Election, ElectionResult, PresidentCandidate, PresidentCandidateBiography, \
    PresidentCandidatePoliticalExperience, PresidentCandidateWorkExperience, PresidentCandidateArticle, \
    PresidentCandidateArticleInformation, MayorCandidate, Moderators, Debates, EuroParliamentCandidate, \
    EuroParliamentCandidatePoliticalExperience, EuroParliamentCandidateWorkExperience, EuroParliamentCandidateEducation, \
    EuroParliamentCandidateConviction, SeimasCandidate
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


class PresidentCandidateBiographyInline(admin.StackedInline):
    model = PresidentCandidateBiography


class PresidentCandidatePoliticalExperienceInline(admin.StackedInline):
    model = PresidentCandidatePoliticalExperience


class PresidentCandidateWorkExperienceInline(admin.StackedInline):
    model = PresidentCandidateWorkExperience


@admin.register(PresidentCandidate)
class PresidentCandidateAdmin(VersionAdmin):
    inlines = [PresidentCandidatePoliticalExperienceInline, PresidentCandidateWorkExperienceInline]
    search_fields = ['name']
    list_display = ['name', 'photo', 'is_active', 'candidate_program_title', 'candidate_program_summary',
                    'candidate_program_link', 'created_at', 'updated_at']
    exclude = ['slug']
    view_on_site = True


@admin.register(SeimasCandidate)
class SeimasCandidateAdmin(VersionAdmin):
    search_fields = ['name']
    list_display = ['name', 'photo', 'is_active', 'email', 'party', 'district', 'created_at', 'updated_at']
    view_on_site = True


@admin.register(MayorCandidate)
class MayorCandidateAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', ]
    list_display = ['first_name', 'last_name', 'email', 'is_active', 'party', 'municipality', 'created_at',
                    'updated_at']
    list_filter = ['is_active', 'municipality', 'party']
    exclude = ['slug']
    view_on_site = True


class EuroParliamentCandidatePoliticalExperienceInline(admin.StackedInline):
    model = EuroParliamentCandidatePoliticalExperience


class EuroParliamentCandidateWorkExperienceInline(admin.StackedInline):
    model = EuroParliamentCandidateWorkExperience


class EuroParliamentCandidateEducationInline(admin.StackedInline):
    model = EuroParliamentCandidateEducation


class EuroParliamentCandidateConvictionInline(admin.StackedInline):
    model = EuroParliamentCandidateConviction


@admin.register(EuroParliamentCandidate)
class MepCandidateAdmin(admin.ModelAdmin):
    inlines = [EuroParliamentCandidatePoliticalExperienceInline, EuroParliamentCandidateWorkExperienceInline,
               EuroParliamentCandidateEducationInline, EuroParliamentCandidateConvictionInline]
    search_fields = ['first_name', 'last_name']
    list_display = ['first_name', 'last_name', 'is_active', 'party', 'created_at', 'updated_at']
    list_filters = ['is_active', 'party']
    exclude = ['slug']
    view_on_site = True


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


@admin.register(Moderators)
class ModeratorsAdmin(VersionAdmin):
    search_fields = ['first_name', 'last_name']
    list_display = ['name', 'photo']
    exclude = ['slug']


def deactivate_debates(ModelAdmin, request, queryset):
    for debate in queryset:
        if debate.is_active == True:
            debate.is_active = False
        debate.save()


deactivate_debates.short_description = "Išjungti pasirinktus debatus"


@admin.register(Debates)
class DebatesAdmin(VersionAdmin):
    search_fields = ['name']
    list_display = ['election_type', 'name', 'tour_id', 'location', 'municipality', 'date', 'time', 'moderator',
                    'is_active',
                    'created_at', 'updated_at']
    list_filter = ['municipality', 'moderator', 'is_active', 'tour_id', 'election_type']
    exclude = ['slug']
    list_select_related = ['municipality', 'moderator']
    autocomplete_fields = ['municipality', 'moderator']
    actions = [deactivate_debates]
