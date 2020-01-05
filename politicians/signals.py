from django.db.models.signals import post_save
from django.dispatch import receiver

from politicians.tasks import get_promise_action_scores
from politicians.models import PromiseAction

@receiver(post_save, sender=PromiseAction)
def on_promise_action_save(sender, instance, **kwargs):
    get_promise_action_scores(instance.pk)