from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from ipware import get_client_ip
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_409_CONFLICT, HTTP_201_CREATED

from web.forms import EmailSubscriptionForm
from web.models import EmailSubscription, OrganizationPartner


def index(request):
    partners = OrganizationPartner.objects.all()
    return render(request, 'web/index.html', {
        'partners': partners
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


def health_check(request):
    return HttpResponse("OK")
