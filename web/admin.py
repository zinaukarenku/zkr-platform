from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from reversion.admin import VersionAdmin

from web.models import OrganizationMember, OrganizationMemberGroup, EmailSubscription, OrganizationPartner, User, \
    PoliticianInfo, Municipality
from zkr import settings
from django.utils.translation import gettext_lazy as _

if not settings.DEBUG:
    admin.site.login = login_required(admin.site.login)

UserAdmin.fieldsets = (
    (None, {'fields': ('username', 'password')}),
    (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'photo')}),
    (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
    (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
)

admin.site.register(User, UserAdmin)


class OrganizationMemberInline(SortableInlineAdminMixin, admin.StackedInline):
    model = OrganizationMember
    raw_id_fields = ['user']
    filter_horizontal = ['municipalities']


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


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(VersionAdmin):
    search_fields = ['name']
    list_display = ['name', 'role', 'group', 'photo']
    list_filter = ['group']
    list_select_related = ['group']


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

    list_select_related = ['seimas_politician', ]
    raw_id_fields = ['seimas_politician', 'user']
    search_fields = ['name']
    list_filter = ['created_at', ]
    date_hierarchy = 'created_at'
    view_on_site = True


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).annotate_with_organization_members_count()

    list_display = ['name', 'organization_members_count']
    exclude = ['slug']
    search_fields = ['name']

    def organization_members_count(self, obj):
        return obj.organization_members_count

    organization_members_count.admin_order_field = 'organization_members_count'
    organization_members_count.short_description = _("Organizacijos narių skaičius savivaldybėje")
