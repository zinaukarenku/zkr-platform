from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import CoreAPICompatInspector, NotHandled
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny

from api.filters import PoliticianInfoListFilters
from api.mixins import APILoggingMixin
from api.permissions import APITokenPermission
from api.serializers import CreateMayorCandidate, PoliticianInfoListSerializer
from elections.models import MayorCandidate
from web.models import PoliticianInfo


class DjangoFilterDescriptionInspector(CoreAPICompatInspector):
    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            result = super(DjangoFilterDescriptionInspector, self).get_filter_parameters(filter_backend)
            for param in result:
                if not param.get('description', ''):
                    param.description = "Filter the returned list by {field_name}".format(field_name=param.name)

            return result

        return NotHandled


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Returns all politicians.",
    filter_inspectors=[DjangoFilterDescriptionInspector],
    security=[]

))
class PoliticianInfoListView(APILoggingMixin, ListAPIView):
    queryset = PoliticianInfo.active.select_related(
        'seimas_politician',
        'seimas_politician__politician_fraction',
        'seimas_politician__politician_fraction__fraction'
    ).order_by(
        'name', 'pk'
    )
    serializer_class = PoliticianInfoListSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = PoliticianInfoListFilters
    filter_fields = ['name', ]


@method_decorator(name='put', decorator=swagger_auto_schema(
    operation_description="Saves mayor candidate.",
))
class CreateMayorCandidateView(APILoggingMixin, UpdateAPIView):
    serializer_class = CreateMayorCandidate
    permission_classes = (APITokenPermission,)
    authentication_classes = []

    def get_object(self):
        return MayorCandidate.objects.filter(
            first_name=self.request.data.get('first_name'),
            last_name=self.request.data.get('last_name'),
            municipality__name=self.request.data.get('municipality'),
        ).first()
