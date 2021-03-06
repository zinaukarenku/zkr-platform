import logging
from typing import List
from urllib.parse import urljoin

from dateutil import parser

from elections.models import ElectionItem, ElectionResultsItem, SingleDistrictElectionResultsItem, \
    CandidateWithVotesItem
from utils.utils import requests_retry_session

logger = logging.getLogger(__name__)


class VRK:
    _BASE_URL = "https://www.vrk.lt/statiniai/puslapiai/rinkimai/"

    def _make_request(self, url: str):
        full_url = urljoin(self._BASE_URL, url)
        logger.info(f"VRK request: {full_url}")

        r = requests_retry_session().get(full_url)
        r.raise_for_status()

        return r.json()

    def elections(self) -> List[ElectionItem]:
        json = self._make_request("rt.json")

        return list(map(
            lambda j: ElectionItem(
                election_id=j['id'],
                vrt_id=j['vrt_id'],
                vr_id=j['vr_id'],
                rt_no=j['rt_no'],
                name=j['vrt_pav'],
                election_date=parser.parse(j['rink_data'])
            ), json['data']
        ))

    def single_district_election_results(self, vr_id: int, rt_no: int, election_id: int, rpg_id: int) \
            -> SingleDistrictElectionResultsItem:
        results_json = self._make_request(
            f"{vr_id}/{rt_no}/{election_id}/rezultatai/rezultataiVienmRpg{rpg_id}.json")

        candidates_json = self._make_request(
            f"{vr_id}/{rt_no}/{election_id}/rezultatai/mobKand.json")['data']

        candidates_lookup_by_id = {c['id']: c for c in candidates_json}

        candidates = list([
            CandidateWithVotesItem(
                name=candidates_lookup_by_id[c['rknd_id']]['pav'],
                candidate_id=c['rknd_id'],
                photo_url=f"{self._BASE_URL}{vr_id}/{rt_no}/{election_id}/mobKand/img/{candidates_lookup_by_id[c['rknd_id']]['img']}",
                party=c.get('iskelusi_partija'),
                postal_votes=c['pastu'],
                ballot_votes=c['balsadezese'],
                percent_ballot_paper=c['proc_nuo_gal_biul'],
                percent_voters=c['proc_nuo_dal_rinkeju']
            ) for c in results_json['data']['balsai'] if c.get('rknd_id')
        ])

        last_update = parser.parse(results_json['header']['date'])

        return SingleDistrictElectionResultsItem(
            election_id=election_id,
            vr_id=vr_id,
            rt_no=rt_no,
            rpg_id=rpg_id,
            candidates=candidates,
            last_update=last_update
        )

    def election_results(self, vr_id: int, rt_no: int, election_id: int) -> ElectionResultsItem:
        json = self._make_request(
            f"{vr_id}/{rt_no}/{election_id}/rezultatai/rezultataiVienmVrt.json")

        rpg_jsons = [x for x in json['data']['biuleteniai'] if x.get('rpg_id')]

        single_districts_results = list(
            map(
                lambda rpg_json: self.single_district_election_results(
                    vr_id=vr_id,
                    rt_no=rt_no,
                    election_id=election_id,
                    rpg_id=rpg_json['rpg_id']
                ),
                rpg_jsons
            )
        )

        return ElectionResultsItem(single_districts_results=single_districts_results)
