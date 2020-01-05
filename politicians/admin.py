from django.contrib import admin
from reversion.admin import VersionAdmin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from politicians.models import Politicians, Promises, PromiseAction, Experience
from web.models import User

# Register your models here.

class ExperienceInline(NestedStackedInline):
    model = Experience
    extra = 0
    fk_name = 'politician'



class PromiseActionInline(NestedStackedInline):
    model = PromiseAction
    extra = 0
    fk_name = 'promise'


class PromisesInline(NestedStackedInline):
    model = Promises
    extra = 0
    fk_name = 'politician'
    inlines = [PromiseActionInline]

@admin.register(Politicians)
class PoliticiansAdmin(NestedModelAdmin):
    inlines = [ExperienceInline, PromisesInline]


    class Media:
        css = {
            'all': ('admin/css/admin.css',)
        }
