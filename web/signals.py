from logging import getLogger

from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver

from seimas.utils import save_image_from_url

logger = getLogger(__name__)


@receiver(user_signed_up)
def save_social_account_photo(request, user, **kwargs):
    if user.photo is not None:
        return False

    social_accounts = SocialAccount.objects.filter(user=user)

    for social_account in social_accounts:
        avatar_url = social_account.get_avatar_url()
        if avatar_url:
            if save_image_from_url(field=user.photo, url=avatar_url):
                return True


