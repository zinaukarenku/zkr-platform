from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import render

from elections.models import Election, PresidentCandidate, PresidentCandidateArticle


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
