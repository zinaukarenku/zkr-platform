from logging import getLogger

from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver

from seimas.models import PoliticianGame
from seimas.utils import save_image_from_url

logger = getLogger(__name__)


@receiver(user_signed_up)
def save_social_account_photo(request, user, **kwargs):
    print("save_social_account_photo")

    if user.photo is not None:
        return False

    social_accounts = SocialAccount.objects.filter(user=user)

    for social_account in social_accounts:
        avatar_url = social_account.get_avatar_url()
        if avatar_url:
            if save_image_from_url(field=user.photo, url=avatar_url):
                return True


@receiver(user_signed_up)
def update_politician_game_user_status(request, user, **kwargs):
    game_id = request.COOKIES.get('politician_game_id', None)
    print("Game id", game_id)

    if game_id:
        game = PoliticianGame.objects.filter(id=game_id, user__isnull=True).first()
        if game:
            game.user = user
            game.save()
