import csv

from elections.models import MayorCandidate
from django.core.management.base import BaseCommand
from django.template.defaultfilters import title

from collections import defaultdict


class Command(BaseCommand):
    help = 'Imports mayor email adresses from local csv'
    file = 'meru_kontaktai.csv'

    def handle(self, *args, **options):
        total_updated = 0
        total_skipped = 0
        contacts = defaultdict(list)

        with open(self.file, newline='') as csvfile:
            f = csv.reader(csvfile, delimiter=';')
            for row in f:
                first_name = title(row[0].strip())
                last_name = title(row[1].strip())
                email = row[3].lower()

                contacts[(first_name,last_name)].append(email)

        mayor_candidates = list(map(lambda x: (x['first_name'], x['last_name']), MayorCandidate.objects.all().values()))
        for mayor_candidate in mayor_candidates:
            emails = contacts[mayor_candidate]
            if len(emails) != 1:
                print(f'SKIPPING EMAIL FOR {mayor_candidate}. HAS {len(emails)} EMAILS: {emails}')
                total_skipped += MayorCandidate.objects.filter(first_name=mayor_candidate[0]).filter(last_name=mayor_candidate[1]).update(email='')
            else:
                email = emails[0]
                total_updated += MayorCandidate.objects.filter(first_name=mayor_candidate[0]).filter(last_name=mayor_candidate[1]).update(email=email)

        print(f'Added emails for {total_updated} mayor candidates')
        print(f'Skipped adding emails for {total_skipped} mayor candidates')
