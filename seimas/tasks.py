import logging
import re
from time import sleep

from celery import shared_task
from django.db import transaction

from seimas.models import ElectionType, Fraction, LegalAct, LegalActDocument, LegalActDocumentType, Party, Politician, \
    PoliticianBusinessTrip, PoliticianDivision, PoliticianFraction, PoliticianParliamentGroup, PoliticianTerm, Session, \
    Term, Committee, PoliticianCommittee, Commission, PoliticianCommission
from seimas.utils import parse_xml, sanitize_text
from utils.utils import requests_retry_session
from web.sendgrid import SendGrid

logger = logging.getLogger(__name__)


@shared_task(soft_time_limit=30)
def fetch_terms():
    req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_seimo_kadencijos")
    req.raise_for_status()

    soup = parse_xml(req.text)
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
    req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_seimo_sesijos?ar_visos=T")
    req.raise_for_status()

    soup = parse_xml(req.text)
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

    soup = parse_xml(req.text)
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
            'bio_url': politician_xml['biografijos_nuoroda']
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
                role=sanitize_text(parliament_group_xml['pareigos']),

                defaults={
                    'name': sanitize_text(parliament_group_xml['parlamentinės_grupės_pavadinimas']),
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
                    'name': sanitize_text(division_xml['padalinio_pavadinimas']),
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
            'kadencijos_id': term.kad_id
        })
        req.raise_for_status()

        soup = parse_xml(req.text)
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


@shared_task(soft_time_limit=600)
def fetch_and_match_fractions_with_politicians():
    statistics = {
        'politician_fractions': {
            'created': 0,
            'updated': 0
        },
        'fractions': {
            'created': 0,
            'updated': 0
        },
    }
    req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_seimo_frakcijos")
    req.raise_for_status()

    soup = parse_xml(req.text)
    terms_xml = soup.find_all('SeimoKadencija')

    for term_xml in terms_xml:
        term = Term.objects.filter(kad_id=term_xml['kadencijos_id']).first()

        if term:
            fractions_xml = term_xml.find_all('SeimoFrakcija')

            for fraction_xml in fractions_xml:
                fraction, is_fraction_created = Fraction.objects.update_or_create(
                    seimas_pad_id=fraction_xml['padalinio_id'],
                    defaults={
                        'name': sanitize_text(fraction_xml['padalinio_pavadinimas']),
                        'short_name': sanitize_text(fraction_xml['padalinio_pavadinimo_santrumpa']),
                    }
                )

                if is_fraction_created:
                    statistics['fractions']['created'] += 1
                else:
                    statistics['fractions']['updated'] += 1

                members_xml = fraction_xml.find_all('SeimoFrakcijosNarys')
                for member_xml in members_xml:
                    politician = Politician.objects.filter(asm_id=member_xml['asmens_id']).first()

                    if politician:
                        _, is_politician_fraction_created = PoliticianFraction.objects.update_or_create(
                            politician=politician,
                            defaults={
                                'position': sanitize_text(member_xml['pareigos']),
                                'fraction': fraction
                            }
                        )

                        if is_politician_fraction_created:
                            statistics['politician_fractions']['created'] += 1
                        else:
                            statistics['politician_fractions']['updated'] += 1

    return statistics


@shared_task(soft_time_limit=600)
def fetch_and_match_committees_with_politicians():
    statistics = {
        'politician_committees': 0,
        'committees': 0
    }
    req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_seimo_komitetai")
    req.raise_for_status()

    soup = parse_xml(req.text)
    committees_xml = soup.find_all('SeimoKomitetas')

    with transaction.atomic():
        Committee.objects.all().delete()

        for committee_xml in committees_xml:
            committee, _ = Committee.objects.update_or_create(
                seimas_pad_id=committee_xml['padalinio_id'],
                defaults={
                    'name': sanitize_text(committee_xml['padalinio_pavadinimas']),
                    'is_main_committee': True
                }
            )

            statistics['committees'] += 1

            members_xml = committee_xml.find_all('SeimoKomitetoNarys')

            for member_xml in members_xml:
                politician = Politician.objects.filter(asm_id=member_xml['asmens_id']).first()

                if politician:
                    _, _ = PoliticianCommittee.objects.update_or_create(
                        politician=politician,
                        committee=committee,
                        defaults={
                            'position': sanitize_text(member_xml['pareigos']),
                        }
                    )

                    statistics['politician_committees'] += 1

        committees_xml = soup.find_all('SeimoKomitetoPakomitetis')

        for committee_xml in committees_xml:
            committee, _ = Committee.objects.update_or_create(
                seimas_pad_id=committee_xml['padalinio_id'],
                defaults={
                    'name': sanitize_text(committee_xml['padalinio_pavadinimas']),
                    'is_main_committee': False
                }
            )

            statistics['committees'] += 1

            members_xml = committee_xml.find_all('SeimoKomitetoPakomitečioNarys')

            for member_xml in members_xml:
                politician = Politician.objects.filter(asm_id=member_xml['asmens_id']).first()

                if politician:
                    _, _ = PoliticianCommittee.objects.update_or_create(
                        politician=politician,
                        committee=committee,
                        defaults={
                            'position': sanitize_text(member_xml['pareigos']),
                        }
                    )

                    statistics['politician_committees'] += 1

    return statistics


@shared_task(soft_time_limit=600)
def fetch_and_match_commissions_with_politicians():
    statistics = {
        'politician_commissions': 0,
        'commissions': 0,
    }
    req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_seimo_komisijos")
    req.raise_for_status()

    soup = parse_xml(req.text)
    commissions_xml = soup.find_all('SeimoKomisija')

    with transaction.atomic():
        Commission.objects.all().delete()
        for commission_xml in commissions_xml:
            commission, _ = Commission.objects.update_or_create(
                seimas_pad_id=commission_xml['padalinio_id'],
                defaults={
                    'name': sanitize_text(commission_xml['padalinio_pavadinimas']),
                }
            )

            statistics['commissions'] += 1

            members_xml = commission_xml.find_all('SeimoKomisijosNarys')

            for member_xml in members_xml:
                politician = Politician.objects.filter(asm_id=member_xml['asmens_id']).first()

                if politician:
                    _, is_politician_commission_created = PoliticianCommission.objects.update_or_create(
                        politician=politician,
                        commission=commission,
                        defaults={
                            'position': sanitize_text(member_xml['pareigos']),
                        }
                    )

                    statistics['politician_commissions'] += 1

    return statistics


@shared_task(soft_time_limit=300)
def fetch_business_trips():
    created = 0
    updated = 0

    req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_sn_komandiruotes")
    req.raise_for_status()

    soup = parse_xml(req.text)
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


@shared_task(soft_time_limit=600)
def fetch_politician_documents():
    created = 0
    updated = 0

    for politician in Politician.active.all():
        req = requests_retry_session().get("http://apps.lrs.lt/sip/p2b.ad_sn_inicijuoti_ta_projektai", params={
            'asmens_id': politician.asm_id
        })
        req.raise_for_status()

        soup = parse_xml(req.text)
        documents_xml = soup.find_all('SeimoNarioPateiktasTeisėsAktoProjektas')

        legal_act_documents = []

        for document_xml in documents_xml:
            legal_act_document_type, _ = LegalActDocumentType.objects.get_or_create(name=document_xml['požymis'].strip())
            legal_act, _ = LegalAct.objects.get_or_create(number=document_xml['registracijos_numeris'])

            legal_act_document, is_created = LegalActDocument.objects \
                .update_or_create(doc_id=document_xml['registracijos_numeris'].lstrip('XIIIP-'),
                                  defaults={
                                      'name': document_xml[
                                          'pavadinimas'].strip(),
                                      'date': document_xml['registracijos_data'].split()[0],
                                      'legal_act': legal_act,
                                      'document_type': legal_act_document_type
                                  })

            legal_act_documents.append(legal_act_document)

            if is_created:
                created += 1
            else:
                updated += 1

        politician.legal_act_documents.set(legal_act_documents, clear=True)
        sleep(2)

    return {
        'created': created,
        'updated': updated
    }


@shared_task(soft_time_limit=120)
def sync_seimas_with_sendgrid():
    politicians = Politician.active.filter(email__isnull=False).exclude(email='')

    contacts_list = list(
        map(
            lambda p: {
                "first_name": p.first_name,
                "last_name": p.last_name,
                "email": p.email
            },
            politicians
        )
    )
    return SendGrid().sync_recipients_to_list(SendGrid.SEIMAS_LIST, contacts_list)
