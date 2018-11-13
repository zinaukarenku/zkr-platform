import logging

from celery import shared_task

from seimas.models import Politician as SeimasPolitician
from web.models import PoliticianInfo, User

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


@shared_task(soft_time_limit=30)
def sync_organization_members_staff_access():
    staff_access_created = User.objects.filter(organization_member__isnull=False,
                                               is_staff=False).update(is_staff=True)

    return {
        'staff_access_created': staff_access_created
    }
