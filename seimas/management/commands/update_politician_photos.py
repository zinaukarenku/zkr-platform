from django.core.files import File
from django.core.management.base import BaseCommand

from seimas.models import Politician


class Command(BaseCommand):
    help = 'Update politician photos'

    def handle(self, *args, **options):
        base_path = 'seimas/static/seimas-photos/'

        for politician in Politician.active.all():
            try:
                file_name = politician.slug.replace('-', '_') + ".jpg"
                with open(f"{base_path}{file_name}", 'rb') as file:
                    politician.photo.save(file_name, File(file))

            except FileNotFoundError:
                print("Unable to find an image for", politician)
            else:
                print("Saved", politician)
