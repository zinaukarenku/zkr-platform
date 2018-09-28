import datetime
from dataclasses import dataclass
from typing import Optional, List

from django.db import models


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
    rknd_id: int
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

    candidates: List[CandidateWithVotesItem]


@dataclass(frozen=True)
class ElectionResultsItem:
    single_districts_results: List[SingleDistrictElectionResultsItem]


class Election(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, blank=True, null=True)

    election_date = models.DateTimeField()

    election_id = models.PositiveIntegerField(unique=True)
    vrt_id = models.PositiveIntegerField()
    vr_id = models.PositiveIntegerField()
    rt_no = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Elections"
        ordering = ['-election_date']

    def __str__(self):
        return self.name
