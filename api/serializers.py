from rest_framework import serializers

from web.models import PoliticianInfo


class PoliticianInfoListSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField()
    short_description = serializers.CharField()

    class Meta:
        model = PoliticianInfo
        fields = ('id', 'name', 'photo', 'short_description')
