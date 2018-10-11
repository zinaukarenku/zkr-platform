from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from reversion.admin import VersionAdmin

from web.models import OrganizationMember, OrganizationMemberGroup, EmailSubscription, OrganizationPartner, User, \
    PoliticianInfo
from zkr import settings

if not settings.DEBUG:
    admin.site.login = login_required(admin.site.login)

admin.site.register(User, UserAdmin)


class OrganizationMemberInline(SortableInlineAdminMixin, admin.TabularInline):
    model = OrganizationMember
    autocomplete_fields = ['user']


@admin.register(OrganizationMemberGroup)
class OrganizationMemberGroupAdmin(SortableAdminMixin, VersionAdmin):
    search_fields = ['name', 'members__name']
    list_display = ['name', 'members_count']
    inlines = [OrganizationMemberInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(members_count=Count('members'))

    def members_count(self, obj):
        return obj.members_count

    members_count.admin_order_field = 'members_count'


@admin.register(OrganizationPartner)
class OrganizationPartnersAdmin(SortableAdminMixin, VersionAdmin):
    search_fields = ['name']
    list_display = ['name', 'logo', 'url']


@admin.register(EmailSubscription)
class EmailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'user_ip', 'user_country', 'user_agent', 'created_at']

    search_fields = ['email', 'user_ip']
    list_filter = ['created_at', 'user_country', ]
    date_hierarchy = 'created_at'


@admin.register(PoliticianInfo)
class PoliticianInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'seimas_politician', 'created_at', 'updated_at']

    list_select_related = ['seimas_politician']
    raw_id_fields = ['seimas_politician']
    search_fields = ['name']
    list_filter = ['created_at', ]
    date_hierarchy = 'created_at'
