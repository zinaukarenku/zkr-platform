from celery import shared_task

from elections.models import Election
from elections.vrk import VRK


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
    pass
    # print(vrk.election_results(election.vr_id, election.rt_no, election.election_id))
    # break
