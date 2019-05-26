from logging import getLogger

from allauth.socialaccount.forms import DisconnectForm
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_409_CONFLICT, HTTP_201_CREATED

from questions.models import Question
from utils.utils import get_request_information
from web.forms import EmailSubscriptionForm
from web.models import EmailSubscription, OrganizationPartner, OrganizationMember, Municipality
from datetime import datetime

logger = getLogger(__name__)


def index(request):
    partners = OrganizationPartner.objects.all()
    voting_ended = datetime.now() > datetime(2019, 5, 26, 20, 0, 0)
    return render(request, 'web/index.html', {
        'partners': partners,
        'voting_ended': voting_ended
    })


def about(request):
    members = OrganizationMember.objects.select_related('group').filter(group__isnull=False).order_by('group__order',
                                                                                                      'order', 'name')

    municipalities_with_members = Municipality.objects.annotate_with_organization_members_count() \
        .exclude(organization_members_count=0) \
        .prefetch_related(Prefetch('organization_members', OrganizationMember.objects.order_by('name'))) \
        .order_by('slug')

    return render(request, 'web/about.html', {
        'members': members,
        'municipalities_with_members': municipalities_with_members
    })


def join_us(request):
    return render(request, 'web/join-us.html')


@require_http_methods(["POST"])
def subscribe(request):
    form = EmailSubscriptionForm(request.POST)
    try:
        if form.is_valid():
            email = form.cleaned_data['email']
            request_info = get_request_information(request)

            EmailSubscription(
                email=email,
                user_ip=request_info.client_ip,
                user_agent=request_info.client_user_agent,
                user_country=request_info.client_country
            ).save()
        else:
            return HttpResponse(status=HTTP_422_UNPROCESSABLE_ENTITY, content='El. paštas neteisingas')
    except IntegrityError:
        return HttpResponse(status=HTTP_409_CONFLICT, content='El. paštas jau registruotas.')

    return HttpResponse(status=HTTP_201_CREATED)


@login_required
def user_profile(request):
    user_questions = Question.objects.filter_questions_by_user_or_for_user(request.user) \
        .select_related_for_display() \
        .annotate_with_last_created_at() \
        .order_by('-last_created_at', 'pk')

    error = None
    if request.method == 'POST':
        disconnect_form = DisconnectForm(request.POST, request=request)

        if disconnect_form.is_valid():
            disconnect_form.save()
        else:
            error = "Unable to disconnect social account. Try again."

    return render(request, 'web/user-profile.html', {
        'error': error,
        'user_questions': user_questions
    })


def health_check(request):
    return HttpResponse("OK")
