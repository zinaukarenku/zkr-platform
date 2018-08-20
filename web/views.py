from allauth.socialaccount.forms import DisconnectForm
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from ipware import get_client_ip
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_409_CONFLICT, HTTP_201_CREATED

from seimas.models import PoliticianGame
from web.forms import EmailSubscriptionForm
from web.models import EmailSubscription, OrganizationPartner, OrganizationMember


def index(request):
    partners = OrganizationPartner.objects.all()
    members = OrganizationMember.objects.select_related('group').all()
    return render(request, 'web/index.html', {
        'partners': partners,
        'members': members
    })


@require_http_methods(["POST"])
def subscribe(request):
    form = EmailSubscriptionForm(request.POST)
    try:
        if form.is_valid():
            email = form.cleaned_data['email']

            user_ip, _ = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', None)

            EmailSubscription(email=email, user_ip=user_ip, user_agent=user_agent).save()
        else:
            return HttpResponse(status=HTTP_422_UNPROCESSABLE_ENTITY, content='Invalid e-mail')
    except IntegrityError:
        return HttpResponse(status=HTTP_409_CONFLICT, content='E-mail is already registered.')

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
