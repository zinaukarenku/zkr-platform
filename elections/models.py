import datetime
from dataclasses import dataclass
from os.path import join
from typing import Optional, List

from django.db import models
from django.utils.text import slugify

from zkr.utils import file_extension


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
        return self.last_results_update is not None

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
