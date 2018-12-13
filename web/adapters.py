from allauth.account.adapter import DefaultAccountAdapter

from web.tasks import send_email_confirmation_letter


class AccountAdapter(DefaultAccountAdapter):
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        activate_url = self.get_email_confirmation_url(
            request,
            emailconfirmation)
        email = emailconfirmation.email_address.email

        send_email_confirmation_letter.delay(email, activate_url)
