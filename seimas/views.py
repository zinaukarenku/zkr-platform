from django.core.paginator import EmptyPage
from django.db.models import Prefetch, Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from ipware import get_client_ip

from questions.models import Question
from seimas.forms import PrizeFrom, PoliticianFiltersForm
from seimas.models import Politician, PoliticianTerm, PoliticianGame, LegalActDocument, PoliticianCommittee
from utils.utils import try_parse_int, PaginatorWithPageLink


def index(request):
    return render(request, 'seimas/index.html')


def politician_game(request):
    if Politician.objects.count() == 0:
        return HttpResponse("No politicians")

    user_ip, _ = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', None)

    politician_id = try_parse_int(request.GET.get('politician', None))
    game_id = request.COOKIES.get('politician_game_id', None)

    prize_form = PrizeFrom(request.POST or None)
    email = None
    if request.method == "POST" and prize_form.is_valid():
        email = prize_form.cleaned_data['email']

    email = email or request.COOKIES.get('email', None) or None

    if email:
        PoliticianGame.objects.filter(id=game_id).exclude(email=email).update(email=email)

    game = None
    if game_id and politician_id:
        game = PoliticianGame.objects.filter(id=game_id, ended__isnull=True) \
            .filter(Q(first_politician__id=politician_id) | Q(second_politician__id=politician_id)).first()
    elif game_id:
        game = PoliticianGame.objects.filter(id=game_id, ended__isnull=True).first()

    if game is None:
        game = PoliticianGame.start_new_game(user=request.user, user_ip=user_ip, user_agent=user_agent)
    elif politician_id:
        selected_politician = Politician.objects.filter(id=politician_id).first()

        game = game.guess_politician(selected_politician)
        if game is None:
            return redirect('seimas_politician_game')

    response = render(request, 'seimas/game.html', {
        'game': game,
        'email': email
    })
    response.set_cookie('politician_game_id', game.id, max_age=300)

    if email:
        response.set_cookie('email', email)

    return response


def politicians(request, page=1):
    filters_form = PoliticianFiltersForm(request.GET)
    politicians_queryset = Politician.active \
        .prefetch_related(Prefetch('politician_committees', PoliticianCommittee.objects.select_related('committee'))) \
        .select_related('politician_fraction',
                        'politician_fraction__fraction'
                        ).order_by('last_name', 'first_name')

    politicians_queryset = filters_form.filter_queryset(politicians_queryset)

    def page_link(page_number):
        if page_number == 1:
            return reverse('seimas_politicians')
        else:
            return reverse('seimas_politicians', kwargs={
                'page': page_number
            })

    politicians_queryset = PaginatorWithPageLink(politicians_queryset, 40, page_link)
    try:
        politicians_queryset = politicians_queryset.page(page)
    except EmptyPage:
        return redirect(page_link(1))

    return render(request, 'seimas/politicians.html', {
        'politicians': politicians_queryset,
        'filters_form': filters_form
    })


def politician(request, slug):
    selected_politician = Politician.objects.filter(slug=slug) \
        .select_related('elected_party', 'politician_fraction', 'politician_fraction__fraction', 'politician_info') \
        .prefetch_related('divisions',
                          'parliament_groups',
                          'business_trips',
                          Prefetch(
                              'politician_terms',
                              PoliticianTerm.objects.select_related('term', 'elected_party', 'election_type')
                          ),
                          Prefetch(
                              'legal_act_documents',
                              LegalActDocument.objects.select_related('legal_act', 'document_type')
                          ),
                          ).first()

    if selected_politician is None:
        raise Http404("Politician does not exist")

    questions = Question.active.select_related('politician', 'politian_answer', 'created_by').filter(
        politician__seimas_politician=selected_politician).order_by('-updated_at')

    return render(request, 'seimas/politician.html', {
        'politician': selected_politician,
        'questions': questions
    })
