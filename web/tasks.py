import logging

from celery import shared_task

from seimas.models import Politician as SeimasPolitician
from web.models import PoliticianInfo

logger = logging.getLogger(__name__)


@shared_task(soft_time_limit=30)
def sync_politician_information():
    seimas_created = 0
    for politician in SeimasPolitician.active.filter(politician_info__isnull=True):
        PoliticianInfo(name=politician.name, seimas_politician=politician).save()
        seimas_created += 1

    return {
        'seimas_created': seimas_created
    }
