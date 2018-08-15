from django.http import HttpResponse


def index(request):
    # print(fetch_business_trips())

    return HttpResponse("OK")
