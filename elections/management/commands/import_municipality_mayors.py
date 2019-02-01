import base64
import csv
import glob
from pprint import pprint

import requests
from django.core.management.base import BaseCommand
from django.template.defaultfilters import title
from django.utils.text import slugify

from web.models import Municipality


class Command(BaseCommand):
    help = 'Imports municipality mayors'

    file = 'merai.csv'
    endpoint = 'https://www.zinaukarenku.lt/api/v1/elections/candidates/mayor/?apiKey={MyApiKey}'

    def get_municipality(self, name):
        return Municipality.objects.filter(name__icontains=name).first()

    def handle(self, *args, **options):
        mapped_regions = {}

        with open(self.file, newline='') as csvfile:
            f = csv.reader(csvfile, delimiter=';')
            for row in f:
                first_name = title(row[1])
                last_name = title(row[2])
                region_str = row[4]
                party = row[5]

                image_file_name = slugify(last_name).upper() + "_" + slugify(first_name).upper()
                image_file_name = image_file_name.replace('-', '_')

                municipality = self.get_municipality(region_str)
                mapped_regions[region_str] = municipality

                photo_file = None
                for file in glob.glob(f"2019SAV_meru_foto/**/*{image_file_name}*", recursive=True):
                    photo_file = file
                    # print(file)

                photo_file_base64 = None
                if photo_file:
                    with open(photo_file, mode='rb') as f:
                        photo_file_base64 = base64.b64encode(f.read()).decode()

                response = requests.put(
                    self.endpoint,
                    json={
                        'first_name': first_name,
                        'last_name': last_name,
                        'municipality': municipality.name,
                        'party': party,
                        'photo': photo_file_base64
                    })

                if not response.ok:
                    print("Fail with photo")
                    requests.put(
                        self.endpoint,
                        json={
                            'first_name': first_name,
                            'last_name': last_name,
                            'municipality': municipality.name,
                            'party': party,
                            'photo': None
                        })
                else:
                    print("Success")

        pprint(mapped_regions)
