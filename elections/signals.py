from django.db.models.signals import post_save
from django.dispatch import receiver

from elections.models import PresidentCandidateArticle, MayorCandidate
from elections.tasks import fetch_president_articles, sync_mayor_candidate_status_with_politician_info


@receiver(post_save, sender=PresidentCandidateArticle)
def on_article_url_saved(sender, instance, **kwargs):
    fetch_president_articles.delay()


@receiver(post_save, sender=MayorCandidate)
def on_mayor_candidate_saved(sender, instance, **kwargs):
    sync_mayor_candidate_status_with_politician_info.delay()
