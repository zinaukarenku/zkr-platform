from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import render

from elections.forms import MayorCandidatesFiltersForm
from elections.models import Election, MayorCandidate, PresidentCandidate, PresidentCandidateArticle, Debates
from questions.models import Question


def elections(request):
    mayor_candidates_filters_form = MayorCandidatesFiltersForm(request.GET)

    mayor_candidates = MayorCandidate.objects.select_related('municipality').order_by('municipality',
                                                                                      'last_name')

    mayor_candidates = mayor_candidates_filters_form.filter_queryset(mayor_candidates)

    debates = Debates.objects.select_related('municipality').order_by('municipality')

    return render(request, 'elections/elections.html', {
        'mayor_candidates': mayor_candidates,
        'mayor_candidates_filters_form': mayor_candidates_filters_form,
        'debates': debates
    })


def mayor_candidates(request):
    mayor_candidates_filters_form = MayorCandidatesFiltersForm(request.GET)

    mayor_candidates = MayorCandidate.objects.select_related('municipality').order_by('municipality',
                                                                                      'last_name')

    mayor_candidates = mayor_candidates_filters_form.filter_queryset(mayor_candidates)

    return render(request, 'elections/mayor/candidates.html', {
        'mayor_candidates': mayor_candidates,
        'mayor_candidates_filters_form': mayor_candidates_filters_form
    })


def mayor_candidate(request, slug):
    candidate = MayorCandidate.objects.select_related('municipality', 'politician_info').filter(slug=slug).first()

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

    debates = Debates.objects.select_related('municipality').order_by('municipality')

    debates = mayor_candidates_filters_form.filter_queryset(debates)

    return render(request, 'elections/debates/debates.html', {
        'mayor_candidates_filters_form': mayor_candidates_filters_form,
        'debates': debates
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
