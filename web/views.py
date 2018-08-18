from django.db.models import Prefetch, Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from ipware import get_client_ip

from seimas.models import Politician, PoliticianTerm, PoliticianGame
from seimas.utils import try_parse_int


def politician_game(request):
    # Temporary hack
    if Politician.objects.count() == 0:
        return HttpResponse("OK")

    user_ip, _ = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', None)

    politician_id = try_parse_int(request.GET.get('politician', None))
    game_id = request.COOKIES.get('politician_game_id', None)
    game = None
    if game_id and politician_id:
        game = PoliticianGame.objects.filter(id=game_id, ended__isnull=True) \
            .filter(Q(first_politician__id=politician_id) | Q(second_politician__id=politician_id)).first()
    elif game_id:
        game = PoliticianGame.objects.filter(id=game_id, ended__isnull=True).first()

    if game is None:
        game = PoliticianGame.start_new_game(user_ip=user_ip, user_agent=user_agent)
    elif politician_id:
        selected_politician = Politician.objects.filter(id=politician_id).first()

        game = game.guess_politician(selected_politician)
        if game is None:
            return redirect('seimas_politician_game')

    response = render(request, 'seimas/game.html', {
        'game': game
    })
    response.set_cookie('politician_game_id', game.id)

    return response


def politicians(request):
    politicians_all = Politician.active.select_related('elected_party')

    return render(request, 'seimas/politicians.html', {
        'politicians': politicians_all
    })


def politician(request, slug):
    selected_politician = Politician.objects.filter(slug=slug) \
        .select_related('elected_party') \
        .prefetch_related('divisions',
                          'parliament_groups',
                          'business_trips',
                          Prefetch('politician_terms',
                                   PoliticianTerm.objects.select_related('term',
                                                                         'elected_party',
                                                                         'election_type'))
                          ).first()

    if selected_politician is None:
        raise Http404("Politician does not exist")

    return render(request, 'seimas/politician.html', {
        'politician': selected_politician
    })
