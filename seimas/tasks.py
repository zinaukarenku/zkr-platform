import logging
import re

from celery import shared_task

from seimas.models import Term, Session, Party, Politician, PoliticianParliamentGroup, PoliticianDivision, \
    PoliticianBusinessTrip, PoliticianTerm, ElectionType
from seimas.utils import requests_retry_session, parse_invalid_xml

logger = logging.getLogger(__name__)


@shared_task(soft_time_limit=30)
def fetch_terms():
    req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_seimo_kadencijos")
    req.raise_for_status()

    soup = parse_invalid_xml(req.text)
    terms_xml = soup.find_all('SeimoKadencija')

    created = 0
    updated = 0
    for term_xml in terms_xml:
        _, is_created = Term.objects.update_or_create(kad_id=term_xml['kadencijos_id'], defaults={
            'name': term_xml['pavadinimas'],
            'start': term_xml['data_nuo'],
            'end': term_xml['data_iki'] or None,
        })

        if is_created:
            created += 1
        else:
            updated += 1

    return {
        'created': created,
        'updated': updated
    }


@shared_task(soft_time_limit=30)
def fetch_sessions():
    req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_seimo_sesijos?p_visos=T")
    req.raise_for_status()

    soup = parse_invalid_xml(req.text)
    terms_xml = soup.find_all('SeimoKadencija')

    created = 0
    updated = 0
    for term_xml in terms_xml:
        kad_id = term_xml['kadencijos_id']
        term = Term.objects.filter(kad_id=kad_id).first()
        if not term:
            continue

        sessions_xml = term_xml.find_all('SeimoSesija')
        for session_xml in sessions_xml:
            _, is_created = Session.objects.update_or_create(ses_id=session_xml['sesijos_id'], defaults={
                'term': term,
                'name': session_xml['pavadinimas'],
                'number': session_xml['numeris'],
                'start': session_xml['data_nuo'],
                'end': session_xml['data_iki'] or None,
            })

            if is_created:
                created += 1
            else:
                updated += 1

    return {
        'created': created,
        'updated': updated
    }


@shared_task(soft_time_limit=600)
def fetch_politicians():
    statistics = {
        'politicians': {
            'created': 0,
            'updated': 0
        },
        'parliament_groups': {
            'created': 0,
            'updated': 0
        },
        'divisions': {
            'created': 0,
            'updated': 0
        }
    }

    req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_seimo_nariai")
    req.raise_for_status()

    soup = parse_invalid_xml(req.text)
    politicians_xml = soup.find_all('SeimoNarys')
    for politician_xml in politicians_xml:
        asm_id = politician_xml['asmens_id']
        is_male = politician_xml['lytis'] == 'V'
        party, _ = Party.objects.update_or_create(name=politician_xml['iškėlusi_partija'])

        defaults = {
            'first_name': politician_xml['vardas'],
            'last_name': politician_xml['pavardė'],
            'is_male': is_male,
            'elected_party': party,
            'start': politician_xml['data_nuo'],
            'end': politician_xml['data_iki'] or None,
            'bio_url': politician_xml['biografija']
        }

        for contact_xml in politician_xml.find_all('Kontaktai', recursive=False):
            contact_type = contact_xml.get('pavadinimas', None) or contact_xml['rūšis']
            value = contact_xml['reikšmė']

            if contact_type == 'Asmeninė interneto svetainė':
                defaults['personal_website'] = value
            elif contact_type == 'El. p.':
                defaults['email'] = value
            elif contact_type == 'Darbo telefonas' or contact_type == 'Mobilus tarnybinis telefonas':
                defaults['phone'] = value
            else:
                logger.warning("Unable to identify polician contact type", exc_info=True, extra={
                    'xml': contact_xml
                })

        politician, is_created = Politician.objects.update_or_create(asm_id=asm_id, defaults=defaults)

        parliament_groups_xml = politician_xml.find_all('Pareigos',
                                                        attrs={'parlamentinės_grupės_id': re.compile(r'\d+')})
        for parliament_group_xml in parliament_groups_xml:
            _, is_group_created = PoliticianParliamentGroup.objects.update_or_create(
                group_id=parliament_group_xml['parlamentinės_grupės_id'],
                politician=politician,
                role=parliament_group_xml['pareigos'],

                defaults={
                    'name': parliament_group_xml['parlamentinės_grupės_pavadinimas'],
                    'start': parliament_group_xml['data_nuo'],
                    'end': parliament_group_xml['data_iki'] or None,
                }
            )

            if is_group_created:
                statistics['parliament_groups']['created'] += 1
            else:
                statistics['parliament_groups']['updated'] += 1

        if is_created:
            statistics['politicians']['created'] += 1
        else:
            statistics['politicians']['updated'] += 1

        divisions_xml = politician_xml.find_all('Pareigos',
                                                attrs={'padalinio_id': re.compile(r'\d+')})
        for division_xml in divisions_xml:
            _, is_division_created = PoliticianDivision.objects.update_or_create(
                pad_id=division_xml['padalinio_id'],
                politician=politician,
                role=division_xml['pareigos'],
                defaults={
                    'name': division_xml['padalinio_pavadinimas'],
                    'start': division_xml['data_nuo'],
                    'end': division_xml['data_iki'] or None,
                }
            )

            if is_division_created:
                statistics['divisions']['created'] += 1
            else:
                statistics['divisions']['updated'] += 1

        if is_created:
            statistics['politicians']['created'] += 1
        else:
            statistics['politicians']['updated'] += 1

    return statistics


@shared_task(soft_time_limit=600)
def fetch_and_match_sessions_with_politicians():
    created = 0
    updated = 0
    for term in Term.objects.all():
        req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_seimo_nariai", params={
            'p_kade_id': term.kad_id
        })
        req.raise_for_status()

        soup = parse_invalid_xml(req.text)
        politicians_xml = soup.find_all('SeimoNarys')

        for politician_xml in politicians_xml:
            politician = Politician.objects.filter(asm_id=politician_xml['asmens_id']).first()
            if politician:
                party, _ = Party.objects.get_or_create(name=politician_xml['iškėlusi_partija'].strip())
                election_type, _ = ElectionType.objects.get_or_create(name=politician_xml['išrinkimo_būdas'].strip())
                _, is_created = PoliticianTerm.objects.update_or_create(politician=politician,
                                                                        term=term,
                                                                        defaults={
                                                                            'start': politician_xml['data_nuo'],
                                                                            'end': politician_xml['data_iki'] or None,
                                                                            'elected_party': party,
                                                                            'election_type': election_type
                                                                        })

                if is_created:
                    created += 1
                else:
                    updated += 1

    return {
        'created': created,
        'updated': updated
    }


@shared_task(soft_time_limit=300)
def fetch_business_trips():
    created = 0
    updated = 0

    req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_seimo_nariu_komandiruotes")
    req.raise_for_status()

    soup = parse_invalid_xml(req.text)
    politicians_xml = soup.find_all('SeimoNarys')

    for politician_xml in politicians_xml:
        politician = Politician.objects.filter(asm_id=politician_xml['asmens_id']).first()

        if not politician:
            continue

        business_trips_xml = politician_xml.find_all('SeimoNarioKomandiruotė')

        for business_trip_xml in business_trips_xml:
            _, is_created = PoliticianBusinessTrip.objects \
                .update_or_create(politician=politician,
                                  name=business_trip_xml['pavadinimas'],
                                  defaults={
                                      'start': business_trip_xml['pradžia'],
                                      'end': business_trip_xml['pabaiga'] or None,
                                      'is_secondment': business_trip_xml['tipas'] == 'Komandiruotė'
                                  })
            if is_created:
                created += 1
            else:
                updated += 1

    return {
        'created': created,
        'updated': updated
    }
