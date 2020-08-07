from django.core.paginator import EmptyPage
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from elections.forms import MayorCandidatesFiltersForm
from elections.models import Debates, Election, EuroParliamentCandidate, MayorCandidate, PresidentCandidate, \
    SeimasCandidate
from questions.models import Question
from utils.utils import PaginatorWithPageLink
from web.models import PoliticianPromise


def elections(request):
    return render(request, 'elections/elections.html')


def elections_2019(request):
    return render(request, 'elections/elections-2019.html')


def seimas_candidates(request, page=1):
    candidates = SeimasCandidate.active.order_by('name', 'pk')

    def page_link(page_number):
        if page_number == 1:
            return reverse('seimas_candidates')
        else:
            return reverse('seimas_candidates', kwargs={
                'page': page_number
            })

    candidates = PaginatorWithPageLink(candidates, page_link, query_params=request.GET.urlencode())
    try:
        candidates = candidates.page(page)
    except EmptyPage:
        return redirect(page_link(1))

    return render(request, 'elections/seimas/candidates.html', {
        'candidates': candidates,
    })


def seimas_candidate(request, slug):
    candidate = SeimasCandidate.objects.select_related(
        'politician_info'
    ).prefetch_related(Prefetch(
        'politician_info__promises',
        PoliticianPromise.objects.select_related('debates')
    )).filter(slug=slug).first()

    if candidate is None:
        raise Http404("Politician does not exist")

    questions = Question.active.select_related('politician', 'politian_answer', 'created_by').filter(
        politician__seimas_candidate=candidate).order_by('-updated_at')

    return render(request, 'elections/mayor/candidate.html', {
        'candidate': candidate,
        'questions': questions,
    })


def mayor_candidates(request, page=1):
    mayor_candidates_filters_form = MayorCandidatesFiltersForm(request.GET)

    candidates = MayorCandidate.active.select_related('municipality').order_by('municipality',
                                                                               'last_name')

    candidates = mayor_candidates_filters_form.filter_queryset(candidates)

    def page_link(page_number):
        if page_number == 1:
            return reverse('mayor_candidates')
        else:
            return reverse('mayor_candidates', kwargs={
                'page': page_number
            })

    candidates = PaginatorWithPageLink(candidates, page_link, query_params=request.GET.urlencode())
    try:
        candidates = candidates.page(page)
    except EmptyPage:
        return redirect(page_link(1))

    return render(request, 'elections/mayor/candidates.html', {
        'mayor_candidates': candidates,
        'mayor_candidates_filters_form': mayor_candidates_filters_form
    })


def mayor_candidate(request, slug):
    candidate = MayorCandidate.objects.select_related(
        'municipality',
        'politician_info'
    ).prefetch_related(Prefetch(
        'politician_info__promises',
        PoliticianPromise.objects.select_related('debates')
    )).filter(slug=slug).first()

    if candidate is None:
        raise Http404("Politician does not exist")

    questions = Question.active.select_related('politician', 'politian_answer', 'created_by').filter(
        politician__mayor_candidate=candidate).order_by('-updated_at')

    return render(request, 'elections/mayor/candidate.html', {
        'candidate': candidate,
        'questions': questions,
    })


def debates_2020(request):
    all_debates = Debates.objects.select_related('municipality', 'moderator').filter(
        created_at__year__gte=2020).order_by('election_type', '-tour_id', '-pk')

    return render(request, 'elections/debates/debates.html', {
        'all_debates': all_debates,
        'year': 2020
    })


def debates_2019(request):
    all_debates = Debates.objects.select_related('municipality', 'moderator').filter(
        created_at__year__lt=2020).order_by('election_type', '-tour_id', '-pk')

    return render(request, 'elections/debates/debates.html', {
        'all_debates': all_debates,
        'year': 2019
    })


def election(request, slug):
    selected_election = Election.active.filter(slug=slug).prefetch_related('results', ).first()

    if selected_election is None:
        raise Http404("Election does not exist")

    return render(request, 'elections/election.html', {
        'election': selected_election
    })


def president_candidates(request):
    candidates = PresidentCandidate.objects.filter(is_active=True)
    return render(request, 'elections/president/candidates.html', {
        'candidates': candidates
    })


def president_candidate(request, slug):
    candidate = PresidentCandidate.objects.select_related("politician_info").filter(slug=slug).first()

    # candidate = PresidentCandidate.objects.

    if candidate is None:
        raise Http404("President candidate does not exist")

    questions = Question.active.select_related('politician', 'politian_answer', 'created_by').filter(
        politician__president_candidate=candidate).order_by('-updated_at')

    return render(request, 'elections/president/candidate.html', {
        'candidate': candidate,
        'questions': questions
    })


def ep_candidates(request):
    candidates = EuroParliamentCandidate.objects.all()
    return render(request, 'elections/ep/candidate.html', {
        'candidates': candidates
    })


def ep_candidate(request, slug):
    candidate = EuroParliamentCandidate.objects.select_related("political_experience", "work_experience").order_by(
        "start")

    if candidate is None:
        raise Http404("European Parliament candidate does not exist")

    questions = Question.active.select_related('politician', 'politian_answer', 'created_by').filter(
        politician__mep_candidate=candidate).order_by('-updated_at')

    return render(request, 'elections/ep/candidate.html', {
        'candidate': candidate,
        'questions': questions
    })
