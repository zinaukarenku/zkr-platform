from django.core.paginator import EmptyPage
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from elections.forms import MayorCandidatesFiltersForm
from elections.models import Election, MayorCandidate, PresidentCandidate, PresidentCandidateArticle, Debates
from questions.models import Question
from utils.utils import PaginatorWithPageLink
from web.models import PoliticianPromise


def elections(request):
    return render(request, 'elections/elections.html')


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


def debates(request):
    mayor_candidates_filters_form = MayorCandidatesFiltersForm(request.GET)

    all_debates = Debates.objects.select_related('municipality', 'moderator').order_by('municipality')

    all_debates = mayor_candidates_filters_form.filter_queryset(all_debates)

    return render(request, 'elections/debates/debates.html', {
        'mayor_candidates_filters_form': mayor_candidates_filters_form,
        'debates': all_debates
    })


def election(request, slug):
    selected_election = Election.active.filter(slug=slug).prefetch_related('results', ).first()

    if selected_election is None:
        raise Http404("Election does not exist")

    return render(request, 'elections/election.html', {
        'election': selected_election
    })


def president_candidates(request):
    candidates = PresidentCandidate.objects.all()
    return render(request, 'elections/president/candidates.html', {
        'candidates': candidates
    })


def president_candidate(request, slug):
    candidate = PresidentCandidate.objects.prefetch_related(
        Prefetch(
            'articles',
            PresidentCandidateArticle.objects.filter(information__isnull=False)
                .select_related('information').order_by('-created_at')
        )
    ).filter(slug=slug).first()

    if candidate is None:
        raise Http404("President candidate does not exist")

    return render(request, 'elections/president/candidate.html', {
        'candidate': candidate
    })
