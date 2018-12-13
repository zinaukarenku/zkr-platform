import logging

from celery import shared_task

from seimas.models import Politician as SeimasPolitician
from web.models import EmailSubscription, PoliticianInfo, User
from web.sendgrid import SendGrid

logger = logging.getLogger(__name__)


@shared_task(soft_time_limit=30)
def send_email_confirmation_letter(email, activate_url):
    return SendGrid().send_letter(
        template_id=SendGrid.VERIFY_EMAIL_TRANSACTIONAL_TEMPLATE,
        emails=[email],
        dynamic_template_data={
            'activate_url': activate_url,
        },
        categories=["Verify email"]
    )


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


@shared_task(soft_time_limit=120)
def sync_newsletter_subscribers():
    contacts_list = list(
        map(
            lambda s: {
                "email": s.email
            },
            EmailSubscription.objects.all()
        )
    )
    return SendGrid().sync_recipients_to_list(6062776, contacts_list)
