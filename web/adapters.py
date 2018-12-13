from allauth.account.adapter import DefaultAccountAdapter

from web.tasks import send_email_confirmation_letter


class AccountAdapter(DefaultAccountAdapter):
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        activate_url = self.get_email_confirmation_url(
            request,
            emailconfirmation)
        email_id = emailconfirmation.email_address.id

        send_email_confirmation_letter.delay(email_id, activate_url)
