from django_filters import rest_framework as filters

from web.models import PoliticianInfo


class PoliticianInfoListFilters(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = PoliticianInfo
        fields = ['name']
