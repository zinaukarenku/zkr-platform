from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from reversion.admin import VersionAdmin

from web.models import OrganizationMember, OrganizationMemberGroup, EmailSubscription, OrganizationPartner


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(SortableAdminMixin, VersionAdmin):
    search_fields = ['name']
    list_filter = ['group']
    list_display = ['name', 'group', 'role', 'photo', 'linkedin_url', 'facebook_url', 'twitter_url']
    list_select_related = ['group']


@admin.register(OrganizationMemberGroup)
class OrganizationMemberGroupAdmin(SortableAdminMixin, VersionAdmin):
    search_fields = ['name']
    list_display = ['name']


@admin.register(OrganizationPartner)
class OrganizationPartnersAdmin(SortableAdminMixin, VersionAdmin):
    search_fields = ['name']
    list_display = ['name', 'logo', 'url']


@admin.register(EmailSubscription)
class EmailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'user_ip', 'user_agent', 'created_at']

    search_fields = ['email', 'user_ip']
    list_filter = ['created_at', ]
    date_hierarchy = 'created_at'
