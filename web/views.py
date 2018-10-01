from logging import getLogger

from allauth.socialaccount.forms import DisconnectForm
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from ipware import get_client_ip
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_409_CONFLICT, HTTP_201_CREATED

from web.forms import EmailSubscriptionForm
from web.models import EmailSubscription, OrganizationPartner, OrganizationMember
from zkr.utils import request_country

logger = getLogger(__name__)


def index(request):
    logger.warning("Meta headers", extra={
        'headers': request.META
    })
    partners = OrganizationPartner.objects.all()
    return render(request, 'web/index.html', {
        'partners': partners
    })


def about(request):
    members = OrganizationMember.objects.select_related('group').order_by('group__order', 'order')
    return render(request, 'web/about.html', {
        'members': members
    })


def join_us(request):
    return render(request, 'web/join-us.html')


@require_http_methods(["POST"])
def subscribe(request):
    form = EmailSubscriptionForm(request.POST)
    try:
        if form.is_valid():
            email = form.cleaned_data['email']

            user_ip, _ = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', None)
            user_country = request_country(request)

            EmailSubscription(email=email, user_ip=user_ip, user_agent=user_agent, user_country=user_country).save()
        else:
            return HttpResponse(status=HTTP_422_UNPROCESSABLE_ENTITY, content='El. paštas neteisingas')
    except IntegrityError:
        return HttpResponse(status=HTTP_409_CONFLICT, content='El. paštas jau registruotas.')

    return HttpResponse(status=HTTP_201_CREATED)


def user_profile(request):
    user = request.user

    if user is None or user.is_authenticated is False:
        return redirect('account_login')

    error = None
    if request.method == 'POST':
        disconnect_form = DisconnectForm(request.POST, request=request)

        if disconnect_form.is_valid():
            disconnect_form.save()
        else:
            error = "Unable to disconnect social account. Try again."

    return render(request, 'web/user-profile.html', {
        'error': error
    })


def health_check(request):
    return HttpResponse("OK")
