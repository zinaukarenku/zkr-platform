from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from seimas.models import Politician, Party
from seimas.tasks import fetch_terms, fetch_sessions, fetch_politicians, fetch_business_trips


def index(request):
    print(fetch_business_trips())

    return HttpResponse("OK")
