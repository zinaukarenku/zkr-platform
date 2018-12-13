import logging
from datetime import timedelta

from allauth.account.models import EmailAddress
from celery import shared_task

from seimas.models import Politician as SeimasPolitician
from utils.utils import django_now
from web.models import PoliticianInfo, User, EmailSubscription
from web.sendgrid import SendGrid

logger = logging.getLogger(__name__)


@shared_task(soft_time_limit=30)
def send_email_confirmation_letter(email_id, activate_url):
    email_address = EmailAddress.objects.get(id=email_id)
    user = email_address.user

    now = django_now()
    if user.last_confirmation_letter_sent is not None and user.last_confirmation_letter_sent + timedelta(
            minutes=5) > now:
        return "Too soon for new confirmation e-mail"

    user.last_confirmation_letter_sent = now
    user.save()

    email = email_address.email

    return SendGrid().send_letter(
        template_id=SendGrid.VERIFY_EMAIL_TRANSACTIONAL_TEMPLATE,
        emails=[email],
        substitutions={
            "%activate_url%": activate_url,
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
