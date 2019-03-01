from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from elections.models import MayorCandidate
from questions.models import Question
from seimas.models import Politician


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"
    protocol = 'https'

    def items(self):
        return ['index', 'about', 'seimas_index', 'seimas_politician_game', ]

    def location(self, item):
        return reverse(item)


class SeimasPoliticianSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.6

    def location(self, obj):
        return reverse('seimas_politician', kwargs={
            'slug': obj.slug
        })

    def items(self):
        return Politician.objects.only('slug', 'updated_at').order_by('-pk')

    @staticmethod
    def lastmod(obj):
        return obj.updated_at


class MayorCandidateSitemap(Sitemap):
    protocol = 'https'
    priority = 0.6

    def items(self):
        return MayorCandidate.active.order_by('-pk')

    def location(self, item):
        return item.profile_url


class QuestionsSitemap(Sitemap):
    protocol = 'https'
    priority = 0.5

    def items(self):
        return Question.active.all().annotate_with_last_created_at().order_by('-pk')

    def location(self, item):
        return item.get_relative_url()

    @staticmethod
    def lastmod(obj):
        return obj.last_created_at
