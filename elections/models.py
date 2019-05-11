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
    party = models.CharField(max_length=280, blank=True, verbose_name=_("Partija"), help_text=_("Jeigu kandidatas - be partijos, nurodykite, kad savarankiškas"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("Kandidato el. paštas")) 
    birth_date = models.DateField(null=True, blank=True, verbose_name=_("Gimimo data"))
    birth_place = models.CharField(max_length=100, blank=True, verbose_name=_("Gimimo vieta"))
    languages = models.CharField(max_length=300, blank=True, verbose_name=_("Užsienio kalbos"))
    hobbies = models.CharField(max_length=500, blank=True, verbose_name=_("Pomėgiai"))
    candidate_program_title = models.CharField(max_length=280, blank=True, verbose_name=_("Kandidato programos pavadinimas"))
    candidate_program_summary = models.TextField(blank=True, verbose_name=_("Kandidato programos santrauka"))
    candidate_program_link = models.URLField(blank=True, verbose_name=_("Kandidato rinkimė programa"))
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



class PresidentCandidateBiography(models.Model):
    candidate = models.ForeignKey(PresidentCandidate, on_delete=models.CASCADE, related_name="biographies")
    bio_period = models.CharField(max_length=15, blank=True, verbose_name=_("Periodas"))
    bio_text = models.TextField(blank=True, verbose_name=_("Biografijos įrašas"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))

    class Meta:
        verbose_name = _("Biografijos įrašas")
        verbose_name_plural = _("Biografijos įrašai")
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.bio_period + " " + self.bio_text
    

class PresidentCandidatePoliticalExperience(models.Model):
    candidate = models.ForeignKey(PresidentCandidate, on_delete=models.CASCADE, related_name="political_experience")
    position = models.CharField(max_length=100, blank=True, verbose_name=_("Pareigos"))
    office = models.CharField(max_length=100, blank=True, verbose_name=_("Institucija"))
    start = models.DateField(null=True, blank=True, verbose_name=_("Pereigų pradžia"))
    end = models.DateField(null=True, blank=True, verbose_name=_("Pereigų pabaiga"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinta"))

    class Meta:
        verbose_name = _("Politinės patirties įrašas")
        verbose_name_plural = _("Politinės patirties įrašai")
        ordering = ["created_at"]

    def __str__(self):
        return self.office + ", " + self.position 
    

class PresidentCandidateWorkExperience(models.Model):
    candidate = models.ForeignKey(PresidentCandidate, on_delete=models.CASCADE, related_name="work_experience")
    position = models.CharField(max_length=100, blank=True, verbose_name=_("Pareigos"))
    office = models.CharField(max_length=100, blank=True, verbose_name=_("Darbovietė"))
    start = models.DateField(null=True, blank=True, verbose_name=_("Pereigų pradžia"))
    end = models.DateField(null=True, blank=True, verbose_name=_("Pereigų pabaiga"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinta"))

    class Meta:
        verbose_name = _("Darbo patirties įrašas")
        verbose_name_plural = _("Darbo patirties įrašai")
        ordering = ["created_at"]

    def __str__(self):
        return self.office + ", " + self.position 

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

class MayorCandidateQuerySet(models.QuerySet):
    pass


class ActiveMayorCandidateManager(models.Manager):
    def get_queryset(self):
        return MayorCandidateQuerySet(self.model, using=self._db).filter(is_active=True)


class MayorCandidate(models.Model):

    def _candidate_photo_file(self, filename):
        ext = file_extension(filename)

        slug = slugify(self.name)
        filename = f"{slug}-photo.{ext}"
        return join('img', 'elections', 'meras-2019', 'candidates', self.municipality.slug, filename)

    is_active = models.BooleanField(db_index=True, verbose_name=_("Aktyvus"), default=True,
                                    help_text=_(
                                        "Indikuoja ar kandidatas į merus matomas merų sąraše bei galima "
                                        "užduoti naują klausimą."))

    first_name = models.CharField(max_length=256, verbose_name=_("Kandidato vardas"))
    last_name = models.CharField(max_length=256, verbose_name=_("Kandidato pavardė"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("Kandidato el. paštas"))

    slug = models.SlugField(unique=True)
    photo = ResizedImageField(blank=True, null=True, upload_to=_candidate_photo_file,
                              crop=['middle', 'center'], size=[256, 256],
                              verbose_name=_("Kandidato nuotrauka"), )
    party = models.CharField(max_length=256, verbose_name=_("Iškėlusi partija arba rinkiminis komitetas"), blank=True)
    municipality = models.ForeignKey("web.Municipality", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinta"))

    objects = MayorCandidateQuerySet.as_manager()
    active = ActiveMayorCandidateManager()

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def profile_url(self):
        return reverse('mayor_candidate', kwargs={'slug': self.slug})

    def get_absolute_url(self):
        return self.profile_url

    @property
    def politician_info_id(self) -> Optional[int]:
        if hasattr(self, 'politician_info') and self.politician_info:
            return self.politician_info.id

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Kandidatas į savivaldybės merus")
        verbose_name_plural = _("Kandidatai į savivaldybės merus")


class MepCandidateQuerySet(models.QuerySet):
    pass

class ActiveMepCandidateManager(models.Manager):
    def get_queryset(self):
        return MepCandidateQuerySet(self.model, using=self._db).filter(is_active=True)


class EuroParliamentCandidate(models.Model):
    def _candidate_photo_file(self, filename):
        ext = file_extension(filename)

        slug = slugify(self.name)
        filename = f"{slug}-photo.{ext}"
        return join('img', 'elections', 'MEP-2019', 'candidates', self.party, filename)

    is_active = models.BooleanField(db_index=True, verbose_name=_("Aktyvus"), default=True,
                                    help_text=_(
                                        "Indikuoja ar kandidatas į Europos Parlamentą matomas kandidatų sąraše bei galima "
                                        "užduoti naują klausimą."))
    slug = models.SlugField(unique=True)
    photo = ResizedImageField(blank=True, null=True, upload_to=_candidate_photo_file,
                              crop=['middle', 'center'], size=[256, 256],
                              verbose_name=_("Kandidato nuotrauka"), )
    party = models.CharField(max_length=256, blank=True, verbose_name=_("Iškėlusi partija arba rinkiminis komitetas"))                                   
    first_name = models.CharField(max_length=256, verbose_name=_("Kandidato vardas"))
    last_name = models.CharField(max_length=256, verbose_name=_("Kandidato pavardė"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("Kandidato el. paštas")) 
    birth_date = models.DateField(null=True, blank=True, verbose_name=_("Gimimo data"))
    birth_place = models.CharField(max_length=100, blank=True, verbose_name=_("Gimimo vieta"))
    languages = models.CharField(max_length=300, blank=True, verbose_name=_("Užsienio kalbos"))
    hobbies = models.CharField(max_length=500, blank=True, verbose_name=_("Pomėgiai"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinta"))

    objects = MepCandidateQuerySet.as_manager()
    active = ActiveMepCandidateManager()

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def profile_url(self):
        return reverse('mep_candidate', kwargs={'slug': self.slug})

    def get_absolute_url(self):
        return self.profile_url

    @property
    def politician_info_id(self) -> Optional[int]:
        if hasattr(self, 'politician_info') and self.politician_info:
            return self.politician_info.id

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Kandidatas į Europos parlamentą")
        verbose_name_plural = _("Kandidatai į Europos parlamentą")


class EuroParliamentCandidateBiography(models.Model):
    candidate = models.ForeignKey(EuroParliamentCandidate, on_delete=models.CASCADE, related_name="biographies")
    bio_period = models.CharField(max_length=15, blank=True, verbose_name=_("Periodas"))
    bio_text = models.TextField(blank=True, verbose_name=_("Biografijos įrašas"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinta"))

    class Meta:
        verbose_name = _("Biografijos įrašas")
        verbose_name_plural = _("Biografijos įrašai")
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.bio_period + " " + self.bio_text

class EuroParliamentCandidatePoliticalExperience(models.Model):
    candidate = models.ForeignKey(EuroParliamentCandidate, on_delete=models.CASCADE, related_name="political_experience")
    position = models.CharField(max_length=100, blank=True, verbose_name=_("Pareigos"))
    office = models.CharField(max_length=100, blank=True, verbose_name=_("Institucija"))
    start = models.DateField(blank=True, verbose_name=_("Pereigų pradžia"))
    end = models.DateField(blank=True, verbose_name=_("Pereigų pabaiga"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinta"))

    class Meta:
        verbose_name = _("Politinės patirties įrašas")
        verbose_name_plural = _("Politinės patirties įrašai")
        ordering = ["created_at"]

    def __str__(self):
        return self.office + ", " + self.position 

class EuroParliamentCandidateWorkExperience(models.Model):
    candidate = models.ForeignKey(EuroParliamentCandidate, on_delete=models.CASCADE, related_name="work_experience")
    position = models.CharField(max_length=100, blank=True, verbose_name=_("Pareigos"))
    office = models.CharField(max_length=100, blank=True, verbose_name=_("Darbovietė"))
    start = models.DateField(blank=True, verbose_name=_("Pereigų pradžia"))
    end = models.DateField(blank=True, verbose_name=_("Pereigų pabaiga"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinta"))

    class Meta:
        verbose_name = _("Darbo patirties įrašas")
        verbose_name_plural = _("Darbo patirties įrašai")
        ordering = ["created_at"]

    def __str__(self):
        return self.office + ", " + self.position 


class Moderators(models.Model):
    def _moderator_photo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.name)

        filename = f"{slug}-photo.{ext}"
        return join('img', 'elections', 'moderators', self.slug, filename)

    slug = models.SlugField(unique=True)
    first_name = models.CharField(max_length=256, verbose_name=_("Moderatoriaus vardas"))
    last_name = models.CharField(max_length=256, verbose_name=_("Moderatoriaus pavardė"))
    photo = ResizedImageField(blank=True, null=True, upload_to=_moderator_photo_file,
                              crop=['middle', 'center'], size=[256, 256],
                              verbose_name=_("Moderatoriaus nuotrauka"), )

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("Moderatorius")
        verbose_name_plural = _("Moderatoriai")
        ordering = ["last_name"]

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class DebatesQuerySet(models.QuerySet):
    pass


class ActiveDebatesManager(models.Manager):
    def get_queryset(self):
        return DebatesQuerySet(self.model, using=self._db).filter(is_active=True)


class Debates(models.Model):
    ELECTION_TYPES = (
        (1, "Merų rinkimai"),
        (2, "Seimo rinkimai"),
        (3, "Europos Parlamento rinkimai"),
        (4, "Prezidento rinkimai"),
        (5, "Savivaldos tarybų rinkimai")
    )
    name = models.CharField(max_length=256, verbose_name=_("Debatų pavadinimas"))
    slug = models.SlugField(unique=True)
    election_type = models.IntegerField(choices=ELECTION_TYPES, verbose_name=_("Rinkimų tipas"))
    location = models.CharField(max_length=256, verbose_name=_("Debatų vieta"),
                                help_text=_("pvz: M. Mažvydo biblioteka"))
    municipality = models.ForeignKey("web.Municipality", on_delete=models.CASCADE, verbose_name=_("Savivaldybė"))
    lat = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=7, verbose_name=_("Platuma"),
                              help_text=_("Google žemėlapiams"))
    lng = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=7, verbose_name=_("Ilguma"),
                              help_text=_("Google žemėlapiams"))
    date = models.DateField(verbose_name=_("Debatų data"))
    time = models.TimeField(verbose_name=_("Debatų laikas"))
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_("Aktyvus"))
    facebook_url = models.URLField(blank=True, verbose_name=_("Debatų Facebook Event puslapio url"))
    youtube_video_url = models.URLField(blank=True, verbose_name=_("Debatų YouTube video url"))
    moderator = models.ForeignKey("Moderators", on_delete=models.CASCADE, verbose_name=_("Moderatorius"))

    tour_id = models.IntegerField(default=1, verbose_name=_("Turo numeris"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sukurta"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atnaujinta"))

    objects = DebatesQuerySet.as_manager()
    active = ActiveDebatesManager()

    class Meta:
        verbose_name = _("Debatai")
        verbose_name_plural = _("Debatai")
        ordering = ["-created_at"]

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name
