import requests
from django.core.management.base import BaseCommand

from web.models import Municipality


# https://www.arcgis.com/home/item.html?id=04ed5d28560749ad8d01005cb0830240#overview
class Command(BaseCommand):
    def handle(self, **options):
        response = requests.get(
            "https://services.arcgis.com/fFwZ4t9mPyCe14FA/arcgis/rest/services/HBContent_SAV/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=OBJECTID%20ASC&resultOffset=0&resultRecordCount=50&quantizationParameters=%7B%22mode%22%3A%22edit%22%7D")
        response.raise_for_status()

        json = response.json()

        for feature in json['features']:
            print(Municipality.objects.update_or_create(name=feature['attributes']['SAV_PAV3']))
