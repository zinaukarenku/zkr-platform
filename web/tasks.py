import logging

from celery import shared_task
from django.urls import reverse

from elections.models import MayorCandidate, SeimasCandidate
from seimas.models import Politician as SeimasPolitician
from web.models import EmailSubscription, PoliticianInfo, User
from web.sendgrid import SendGrid

logger = logging.getLogger(__name__)


@shared_task(soft_time_limit=30)
def send_email_confirmation_letter(email, activate_url):
    SendGrid().send_letter(
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
    mayors_created = 0
    seimas_candidate_created = 0
    for politician in SeimasPolitician.active.filter(politician_info__isnull=True):
        PoliticianInfo(name=politician.name, seimas_politician=politician).save()
        seimas_created += 1

    for candidate in MayorCandidate.objects.filter(politician_info__isnull=True):
        PoliticianInfo(name=candidate.name, mayor_candidate=candidate).save()
        mayors_created += 1

    for candidate in SeimasCandidate.objects.filter(politician_info__isnull=True):
        PoliticianInfo(name=candidate.name, seimas_candidate=candidate).save()
        seimas_candidate_created += 1

    return {
        'seimas_created': seimas_created,
        'mayors_created': mayors_created,
        'seimas_candidate_created': seimas_candidate_created,
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
    return SendGrid().sync_recipients_to_list(SendGrid.NEWSLETTER_SUBSCRIBERS_LIST, contacts_list)


@shared_task(soft_time_limit=30)
def send_registration_email(request, email, secret):
    url = request.build_absolute_uri(reverse('questions_list_after_registration', args=[secret]))
    SendGrid().send_letter(
        template_id=SendGrid.INVITE_FOR_REGISTRATION_TRANSACTIONAL_TEMPLATE,
        emails=[email],
        dynamic_template_data={
            'registration_url': url,
        },
        categories=["Invite for registration"]
    )
