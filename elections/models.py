import datetime
from dataclasses import dataclass
from os.path import join
from typing import Optional, List

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField

from utils.utils import file_extension


@dataclass(frozen=True)
class ElectionItem:
    election_id: int
    vrt_id: int
    vr_id: int
    rt_no: int

    name: str
    election_date: datetime


@dataclass(frozen=True)
class CandidateWithVotesItem:
    name: str
    candidate_id: int
    photo_url: str
    party: Optional[str]

    postal_votes: int
    ballot_votes: int

    percent_ballot_paper: int
    percent_voters: int


@dataclass(frozen=True)
class SingleDistrictElectionResultsItem:
    election_id: int
    vr_id: int
    rt_no: int
    rpg_id: int
    last_update: datetime

    candidates: List[CandidateWithVotesItem]


@dataclass(frozen=True)
class ElectionResultsItem:
    single_districts_results: List[SingleDistrictElectionResultsItem]


class ElectionsQuerySet(models.QuerySet):
    pass


class ActiveElectionsManager(models.Manager):
    def get_queryset(self):
        return ElectionsQuerySet(self.model, using=self._db).filter(is_active=True, slug__isnull=False)


class Election(models.Model):
    name = models.CharField(max_length=256)

    seo_title = models.CharField(max_length=256, blank=True, default='')
    seo_description = models.CharField(max_length=512, blank=True, default='')
    slug = models.SlugField(unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=False, db_index=True)

    election_date = models.DateTimeField()

    election_id = models.PositiveIntegerField(unique=True)
    vrt_id = models.PositiveIntegerField()
    vr_id = models.PositiveIntegerField()
    rt_no = models.PositiveIntegerField()

    last_results_update = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ElectionsQuerySet.as_manager()
    active = ActiveElectionsManager()

    @property
    def is_results_available(self):
        return self.last_results_update is not None and any([r for r in self.results.all() if r.total_votes()])

    class Meta:
        verbose_name_plural = "Elections"
        ordering = ['-election_date']

    def __str__(self):
        return self.name


class ElectionResult(models.Model):
    def _candidate_photo_file(self, filename):
        ext = file_extension(filename)

        slug = slugify(self.name)
        filename = f"{slug}-photo.{ext}"
        return join('img', 'elections', self.election.slug, 'candidates', filename)

    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="results")

    name = models.CharField(max_length=256)
    party = models.CharField(max_length=256, null=True, blank=True)
    photo = models.ImageField(null=True, blank=True, upload_to=_candidate_photo_file)

    candidate_id = models.PositiveIntegerField()

    postal_votes = models.PositiveIntegerField()
    ballot_votes = models.PositiveIntegerField()

    percent_ballot_paper = models.DecimalField(max_digits=5, decimal_places=2)
    percent_voters = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Election results"
        ordering = ['-percent_ballot_paper']
        unique_together = ['election', 'candidate_id']

    def total_votes(self):
        return self.postal_votes + self.ballot_votes

    def __str__(self):
        return self.name


class PresidentCandidate(models.Model):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(force_insert, force_update, using, update_fields)

    def _candidate_photo_file(self, filename):
        ext = file_extension(filename)

        slug = slugify(self.name)
        filename = f"{slug}-photo.{ext}"
        return join('img', 'elections', 'president-2019', 'candidates', filename)

    name = models.CharField(max_length=256, verbose_name=_("Kandidato vardas"))
    slug = models.SlugField(unique=True)
    photo = models.ImageField(upload_to=_candidate_photo_file, verbose_name=_("Kandidato nuotrauka"))
    short_description = models.CharField(max_length=280, blank=True, verbose_name=_("Trumpas aprašymas"))

    candidate_program = models.URLField(blank=True, verbose_name=_("Kandidato rinkimė programa"))
    facebook = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinta"))

    class Meta:
        verbose_name = _("Kandidatas į prezidentus")
        verbose_name_plural = _("Kandidatai į prezidentus")

    def get_absolute_url(self):
        return reverse('president_candidate', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class PresidentCandidateArticle(models.Model):
    candidate = models.ForeignKey(PresidentCandidate, on_delete=models.CASCADE, related_name="articles")
    url = models.URLField(verbose_name=_("Naujienos nuoroda"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))

    class Meta:
        verbose_name = _("Naujiena apie kandidatą į prezidentus")
        verbose_name_plural = _("Naujienos apie kandidatus į prezidentus")
        unique_together = [('candidate', 'url')]
        ordering = ['-created_at']

    def __str__(self):
        return self.url


class PresidentCandidateArticleInformation(models.Model):
    def _article_photo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.title)

        filename = f"{slug}-photo.{ext}"
        candidate = self.article.candidate.slug
        return join('img', 'elections', 'president-2019', 'candidates', 'articles', candidate, filename)

    article = models.OneToOneField(PresidentCandidateArticle, on_delete=models.CASCADE, related_name="information",
                                   verbose_name=_("Naujiena"))
    url = models.URLField()

    title = models.CharField(max_length=256, verbose_name=_("Pavadinimas"))
    site = models.CharField(max_length=256, blank=True, verbose_name=_("Šaltinis"))
    image = ResizedImageField(blank=True, null=True, upload_to=_article_photo_file,
                              crop=['middle', 'center'], size=[256, 256],
                              verbose_name=_("Nuotrauka"))
    description = models.TextField(verbose_name=_("Aprašymas"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.url
