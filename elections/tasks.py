from celery import shared_task
from requests import HTTPError

from elections.models import Election, ElectionResult
from elections.vrk import VRK
from zkr.utils import save_image_from_url


@shared_task(soft_time_limit=60)
def fetch_vrk_elections():
    created = 0
    updated = 0

    vrk = VRK()
    for election in vrk.elections():
        _, is_created = Election.objects.update_or_create(
            election_id=election.election_id,
            defaults={
                'name': election.name,
                'election_date': election.election_date,
                'vrt_id': election.vrt_id,
                'vr_id': election.vr_id,
                'rt_no': election.rt_no
            }
        )

        if is_created:
            created += 1
        else:
            updated += 1

    return {
        'created': created,
        'updated': updated
    }


@shared_task(soft_time_limit=220)
def fetch_vrk_election_results():
    created = 0
    updated = 0
    photos_saved = 0

    vrk = VRK()

    for election in Election.active.all():
        try:
            election_results = vrk.election_results(election.vr_id, election.rt_no, election.election_id)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                continue

            raise ex

        last_update = None
        for election_result in election_results.single_districts_results:
            last_update = election_result.last_update
            for candidate in election_result.candidates:
                result, is_created = ElectionResult.objects.update_or_create(
                    election=election,
                    candidate_id=candidate.candidate_id,
                    defaults={
                        'name': candidate.name,
                        'party': candidate.party,
                        'postal_votes': candidate.postal_votes,
                        'ballot_votes': candidate.ballot_votes,
                        'percent_ballot_paper': candidate.percent_ballot_paper,
                        'percent_voters': candidate.percent_voters,
                    }
                )

                if not result.photo and candidate.photo_url:
                    if save_image_from_url(field=result.photo, url=candidate.photo_url):
                        photos_saved += 1

                if is_created:
                    created += 1
                else:
                    updated += 1

        if last_update != election.last_results_update:
            election.last_results_update = last_update
            election.save()

    return {
        'created': created,
        'updated': updated,
        'photos_saved': photos_saved
    }
