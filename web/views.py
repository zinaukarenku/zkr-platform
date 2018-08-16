from django.http import Http404
from django.shortcuts import render

from seimas.models import Politician


def politicians(request):
    politicians_all = Politician.active.select_related('elected_party')

    return render(request, 'seimas/politicians.html', {
        'politicians': politicians_all
    })


def politician(request, slug):
    selected_politician = Politician.objects.filter(slug=slug) \
        .select_related('elected_party').prefetch_related('divisions', 'parliament_groups', 'business_trips').first()

    if selected_politician is None:
        raise Http404("Politician does not exist")

    return render(request, 'seimas/politician.html', {
        'politician': selected_politician
    })
