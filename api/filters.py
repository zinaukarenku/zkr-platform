from django_filters import rest_framework as filters

from web.models import PoliticianInfo
from zkr import settings


class PoliticianInfoListFilters(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr='unaccent__icontains' if settings.IS_POSTGRES_AVAILABLE else 'icontains'
    )

    class Meta:
        model = PoliticianInfo
        fields = ['name']
