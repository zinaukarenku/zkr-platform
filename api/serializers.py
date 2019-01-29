from rest_framework import serializers

from api.fields import Base64ImageField
from elections.models import MayorCandidate
from web.models import PoliticianInfo, Municipality


class PoliticianInfoListSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField()
    short_description = serializers.CharField()

    class Meta:
        model = PoliticianInfo
        fields = ('id', 'name', 'photo', 'short_description')


class CreateMayorCandidate(serializers.ModelSerializer):
    photo = Base64ImageField(max_length=None, allow_null=True, represent_in_base64=True)

    municipality = serializers.SlugRelatedField(slug_field='name',
                                                queryset=Municipality.objects.all())

    class Meta:
        model = MayorCandidate
        fields = [
            'first_name',
            'last_name',
            'photo',
            'party',
            'municipality',
        ]
