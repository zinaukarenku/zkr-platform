import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand

from seimas.tasks import fetch_terms, fetch_sessions, fetch_politicians, fetch_and_match_sessions_with_politicians, \
    fetch_business_trips, fetch_politician_documents

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetches all seimas data and saves politician photos'

    def handle(self, *args, **options):
        fetch_terms()
        fetch_sessions()
        fetch_politicians()

        call_command('update_politician_photos')

        fetch_and_match_sessions_with_politicians()
        fetch_business_trips()
        fetch_politician_documents()
