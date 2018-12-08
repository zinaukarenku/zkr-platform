from django.db.models.signals import post_save
from django.dispatch import receiver

from elections.models import PresidentCandidateArticle
from elections.tasks import fetch_president_articles


@receiver(post_save, sender=PresidentCandidateArticle)
def on_article_url_saved(sender, instance, **kwargs):
    fetch_president_articles.delay()
