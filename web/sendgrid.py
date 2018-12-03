import json
from collections import namedtuple
from logging import getLogger

import python_http_client
import sendgrid
from requests.structures import CaseInsensitiveDict

from zkr import settings

logger = getLogger(__name__)

SendGridRecipient = namedtuple('SendGridRecipient', 'email id')


class SendGrid:
    def __init__(self, api_key=settings.SENDGRID_API_KEY) -> None:
        self.sg = sendgrid.SendGridAPIClient(apikey=api_key)

    def _list_recipients(self, list_id):
        page = 1

        while True:
            try:
                existing = self.sg.client.contactdb.lists._(list_id).recipients.get(
                    query_params={'page': page, 'page_size': 1000})

                for r in json.loads(existing.body)['recipients']:
                    yield SendGridRecipient(r['email'], r['id'])
                page += 1
            except python_http_client.exceptions.NotFoundError:
                break

    def _all_recipients(self):
        page = 1

        while True:
            try:
                existing = self.sg.client.contactdb.recipients.get(
                    query_params={'page': page, 'page_size': 1000})

                for r in json.loads(existing.body)['recipients']:
                    yield SendGridRecipient(r['email'], r['id'])
                page += 1
            except python_http_client.exceptions.NotFoundError:
                break

    def _delete_recipient_from_list(self, list_id, recipient_ids):
        if len(recipient_ids) > 0:
            self.sg.client.contactdb.lists._(list_id).recipients.delete(request_body=recipient_ids)

        return len(recipient_ids)

    def _delete_recipients(self, recipient_ids):
        if len(recipient_ids) > 0:
            self.sg.client.contactdb.recipients.delete(request_body=recipient_ids)

        return len(recipient_ids)

    def _create_recipients(self, recipients):
        if len(recipients) == 0:
            return {
                'error_count': 0,
                'recipients_new_count': 0,
                'recipients_updated_count': 0,
            }

        create_recipients_response = self.sg.client.contactdb.recipients.patch(request_body=recipients)

        response = json.loads(create_recipients_response.body)

        errors = response['errors']
        for error in errors:
            emails = '\n'.join([recipients[i]['email'] for i in error['error_indices']])
            logger.warning(error['message'], exc_info=True, extra={
                'emails': emails
            })

        return {
            'error_count': response['error_count'],
            'recipients_new_count': response['new_count'],
            'recipients_updated_count': response['updated_count'],
        }

    def _add_recipients_to_list(self, list_id, recipient_ids):
        if len(recipient_ids) > 0:
            self.sg.client.contactdb.lists._(list_id).recipients.post(request_body=recipient_ids)
        return len(recipient_ids)

    def sync_recipients_to_list(self, list_id, recipients, delete_recipients=True):
        stats = {}
        stats['create_recipients'] = self._create_recipients(recipients)

        all_recipients_lookup = CaseInsensitiveDict({r.email: r.id for r in self._all_recipients()})
        list_recipients = list(self._list_recipients(list_id))

        recipients_not_assigned_to_list_lookup = CaseInsensitiveDict(
            {r['email']: all_recipients_lookup[r['email']] for r in recipients if r['email'] in all_recipients_lookup})
        for recipient in list_recipients:
            recipients_not_assigned_to_list_lookup.pop(recipient.email, None)

        recipient_ids_to_add = list(recipients_not_assigned_to_list_lookup.values())
        stats['add_recipients_to_list'] = self._add_recipients_to_list(list_id, recipient_ids_to_add)

        if delete_recipients:
            contact_to_delete_lookup = CaseInsensitiveDict({c.email: c.id for c in list_recipients})
            for recipient in recipients:
                contact_to_delete_lookup.pop(recipient['email'], None)

            recipients_ids_to_delete = list(contact_to_delete_lookup.values())

            stats['delete_recipient_from_list'] = self._delete_recipient_from_list(list_id, recipients_ids_to_delete)
            stats['delete_recipients'] = self._delete_recipients(recipients_ids_to_delete)

        return stats

    def _send_letter(self, data):
        return self.sg.client.mail.send.post(request_body=data)

    def send_letter(self, template_id, email, subject=None, substitutions=None, categories=None, html_content=None):
        substitutions = substitutions or {}
        data = {
            "personalizations": [
                {
                    "to": [
                        {
                            "email": email
                        }
                    ],
                    "substitutions": substitutions,
                }
            ],
            "from": {
                "name": settings.DEFAULT_FROM_EMAIL,
                "email": settings.EMAIL_FROM,
            },
            "categories": categories,
            'subject': subject,
            "template_id": template_id
        }

        if html_content:
            data["content"] = [{
                "type": "text/html",
                "value": html_content
            }]

        return self._send_letter(data)
