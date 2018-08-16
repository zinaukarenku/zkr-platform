from django.http import Http404
from django.shortcuts import render

from seimas.models import Politician


def politicians(request):
    politicians_all = Politician.active.select_related('elected_party')

    return render(request, 'seimas/politicians.html', {
        'politicians': politicians_all
    })


def politician(request, slug):
    selected_politician = Politician.objects.filter(slug=slug).first()

    if selected_politician is None:
        raise Http404("Politician does not exist")

    return render(request, 'seimas/politicians.html', {
        'politician': selected_politician
    })
