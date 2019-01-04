import logging
import random
import uuid
from collections import namedtuple
from os.path import join
from random import randint
from typing import Optional

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from utils.utils import file_extension, django_now, add_url_params
from zkr import settings
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class Term(models.Model):
    name = models.CharField(max_length=50)
    start = models.DateField()
    end = models.DateField(null=True, blank=True)

    kad_id = models.IntegerField(unique=True, help_text="Kadencijos id is used internally in seimas web")

    class Meta:
        verbose_name_plural = "Terms"
        ordering = ['-start']

    def __str__(self):
        return self.name


class Session(models.Model):
    name = models.CharField(max_length=50)
    number = models.PositiveSmallIntegerField()

    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="sessions")

    start = models.DateField()
    end = models.DateField(null=True, blank=True)

    ses_id = models.IntegerField(unique=True, help_text="Sesijos id is used internally in seimas web")

    class Meta:
        verbose_name_plural = "Sessions"
        ordering = ['term', 'number']

    def __str__(self):
        return self.name


class Fraction(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True)
    short_name = models.CharField(max_length=32)

    seimas_pad_id = models.IntegerField(unique=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.short_name)

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name_plural = _("Frakcijos")
        verbose_name = _("Frakcija")
        ordering = ['name']

    def __str__(self):
        return self.name


class Commission(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True)

    seimas_pad_id = models.IntegerField(unique=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name_plural = _("Komisijos")
        verbose_name = _("Komsija")
        ordering = ['name']

    def __str__(self):
        return self.name


class Committee(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True)
    is_main_committee = models.BooleanField(default=True)

    seimas_pad_id = models.IntegerField(unique=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name_plural = _("Komitetai")
        verbose_name = _("Komitetas")
        ordering = ['name']

    def __str__(self):
        return self.name


class Party(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name_plural = "Parties"

    def __str__(self):
        return self.name


class ElectionType(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name_plural = "Election types"

    def __str__(self):
        return self.name


class LegalAct(models.Model):
    number = models.CharField(max_length=32, unique=True)

    class Meta:
        verbose_name_plural = "Legal acts"

    def __str__(self):
        return self.number


class LegalActDocumentType(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name_plural = "Legal act document types"

    def __str__(self):
        return self.name


class LegalActDocument(models.Model):
    doc_id = models.IntegerField(unique=True)
    legal_act = models.ForeignKey(LegalAct, on_delete=models.CASCADE, related_name='documents')
    document_type = models.ForeignKey(LegalActDocumentType, on_delete=models.CASCADE, related_name='documents')

    name = models.CharField(max_length=1024)
    date = models.DateField(db_index=True)

    def url(self):
        return f"http://www3.lrs.lt/pls/inter/dokpaieska.showdoc_l?p_id={self.doc_id}"

    class Meta:
        verbose_name_plural = "Legal act documents"
        ordering = ['-date', '-doc_id']

    def __str__(self):
        return f"{self.doc_id} - {self.name}"


class PoliticianQuerySet(models.QuerySet):
    pass


class ActivePoliticianManager(models.Manager):
    def get_queryset(self):
        return PoliticianQuerySet(self.model, using=self._db).filter(is_active=True)


class Politician(models.Model):
    def _politician_photo_file(self, filename):
        ext = file_extension(filename)

        filename = f"{self.slug}-photo.{ext}"
        return join('img', 'seimas', 'politician', self.slug, filename)

    asm_id = models.IntegerField(unique=True, help_text="Asmens id is used internally in seimas web")

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    is_active = models.BooleanField(default=True, db_index=True)

    photo = models.ImageField(null=True, blank=True, upload_to=_politician_photo_file)

    is_male = models.BooleanField(default=True)

    elected_party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="politicians")
    legal_act_documents = models.ManyToManyField(LegalActDocument, related_name="politicians")

    start = models.DateField()
    end = models.DateField(blank=True, null=True)

    bio_url = models.URLField(null=True, blank=True)

    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=12, null=True, blank=True)
    personal_website = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PoliticianQuerySet.as_manager()
    active = ActivePoliticianManager()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    @property
    def politician_fraction_nullable(self):
        if hasattr(self, 'politician_fraction'):
            return self.politician_fraction

    @property
    def profile_url(self):
        return reverse('seimas_politician', kwargs={'slug': self.slug})

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def short_description(self) -> Optional[str]:
        return self.fraction_name

    @property
    def fraction_name(self) -> Optional[str]:
        politician_fraction_nullable = self.politician_fraction_nullable

        if politician_fraction_nullable:
            return politician_fraction_nullable.fraction.name

    @property
    def committees_names_text(self) -> str:
        return ', '.join(
            map(
                lambda c: c.committee.name,
                self.politician_committees.all())
        )

    @property
    def politician_info_id(self) -> Optional[str]:
        if hasattr(self, 'politician_info') and self.politician_info:
            return self.politician_info.id

    class Meta:
        verbose_name_plural = "Politicians"

    def __str__(self):
        return self.name


class PoliticianFraction(models.Model):
    fraction = models.ForeignKey(Fraction, on_delete=models.CASCADE, related_name="politicians")
    politician = models.OneToOneField(Politician, on_delete=models.CASCADE, related_name="politician_fraction")

    position = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = "Politician fractions"

    def __str__(self):
        return str(self.politician)


class PoliticianCommittee(models.Model):
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name="politicians")
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE, related_name="politician_committees")

    position = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = _("Politikų komitetai")
        unique_together = ['committee', 'politician']

    def __str__(self):
        return str(self.politician)


class PoliticianCommission(models.Model):
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE, related_name="politicians")
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE, related_name="politician_commissions")

    position = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = _("Politikų komisijos")
        verbose_name = _("Politikų komisija")
        unique_together = ['commission', 'politician']

    def __str__(self):
        return str(self.politician)


class PoliticianTerm(models.Model):
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE, related_name="politician_terms")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="politician_terms")

    start = models.DateField()
    end = models.DateField(null=True, blank=True)

    elected_party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="politician_terms")
    election_type = models.ForeignKey(ElectionType, on_delete=models.CASCADE, related_name="politician_terms")

    class Meta:
        verbose_name_plural = "Politician terms"
        ordering = ['politician', 'term']
        unique_together = ['politician', 'term']

    def __str__(self):
        return f"{self.politician} in {self.term}"


class PoliticianDivision(models.Model):
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE, related_name="divisions")

    name = models.CharField(max_length=255)
    role = models.CharField(max_length=128)

    start = models.DateField()
    end = models.DateField(null=True, blank=True)

    pad_id = models.IntegerField(help_text="padalinio_id is used internally in seimas web")

    class Meta:
        verbose_name_plural = "Politician divisions"
        ordering = ['politician', 'start']
        unique_together = ['politician', 'pad_id', 'role']

    def __str__(self):
        return f"{self.politician} {self.name} group as {self.role}"


class PoliticianParliamentGroup(models.Model):
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE, related_name="parliament_groups")

    name = models.CharField(max_length=255)
    role = models.CharField(max_length=128)

    start = models.DateField()
    end = models.DateField(null=True, blank=True)

    group_id = models.IntegerField(help_text="parlamentinės_grupės_id is used internally in seimas web")

    class Meta:
        verbose_name_plural = "Politician parliament groups"
        ordering = ['politician', '-start']
        unique_together = ['politician', 'group_id', 'role']

    def __str__(self):
        return f"{self.politician} {self.name} group as {self.role}"


class PoliticianBusinessTrip(models.Model):
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE, related_name="business_trips")

    name = models.CharField(max_length=255)

    start = models.DateField()
    end = models.DateField(null=True, blank=True)

    is_secondment = models.BooleanField(default=False, help_text="True stands for Komandiruotė, False for Kelionė")

    class Meta:
        verbose_name_plural = "Politician business trips"
        ordering = ['politician', '-start']
        unique_together = ['politician', 'name']

    def __str__(self):
        return f"{self.politician} business trip {self.name}"


class PoliticianGameQuerySet(models.QuerySet):
    def annotate_with_politicians_answered_count(self):
        return self.annotate(politicians_answered_count=models.Count('answered_politicians'))


class PoliticianGame(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(null=True, blank=True)

    ended = models.DateTimeField(null=True, blank=True)

    answered_politicians = models.ManyToManyField(Politician, blank=True)

    first_politician = models.ForeignKey(Politician, on_delete=models.CASCADE, related_name="+")
    second_politician = models.ForeignKey(Politician, on_delete=models.CASCADE, related_name="+")
    correct_politician = models.ForeignKey(Politician, on_delete=models.CASCADE, related_name="+")

    lost_on_politician = models.ForeignKey(Politician, null=True, blank=True, on_delete=models.CASCADE,
                                           related_name="game_lost_politicians")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True,
                             related_name="politician_games")
    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PoliticianGameQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "Politicians game"
        ordering = ['-created_at']

    @staticmethod
    def generate_politicians_pair(is_male, answered_politician_ids):
        politicians_queryset = Politician.active.filter(photo__isnull=False, is_male=is_male) \
            .exclude(id__in=answered_politician_ids).exclude(photo='')
        politicians_count = politicians_queryset.count()
        if politicians_count >= 2:
            politician1, politician2 = politicians_queryset.order_by('?')[:2]

            return politician1, politician2
        else:
            return None, None

    @staticmethod
    def generate_random_politician_pair(answered_politician_ids):
        is_male = randint(0, 10) >= 4

        politician1, politician2 = PoliticianGame.generate_politicians_pair(is_male=is_male,
                                                                            answered_politician_ids=answered_politician_ids)
        if politician1 and politician2:
            return politician1, politician2

        return PoliticianGame.generate_politicians_pair(is_male=not is_male,
                                                        answered_politician_ids=answered_politician_ids)

    @property
    def answered_count(self):
        return self.answered_politicians.all().count()

    def is_game_ended(self):
        if self.ended:
            return True

        politician1, politician2 = self.generate_random_politician_pair(self.answered_politicians.all())

        return politician1 is None

    def is_game_lost(self):
        return self.lost_on_politician is None

    @staticmethod
    def start_new_game(user, user_ip, user_agent):
        game = PoliticianGame()

        game.user = user if user.is_authenticated else None
        game.user_ip = user_ip
        game.user_agent = user_agent

        game.first_politician, game.second_politician = PoliticianGame.generate_random_politician_pair([])
        game.correct_politician = random.choice([game.first_politician, game.second_politician])
        game.save()

        return game

    def guess_politician(self, selected_politician):
        if not self.first_politician.id != selected_politician.id \
                and not self.second_politician.id != selected_politician.id:
            logger.warning("Selected politician id doesn't match", exc_info=True)
            return None

        if selected_politician.id != self.correct_politician.id:
            self.ended = django_now()
            self.lost_on_politician = self.correct_politician
            self.save()

            return self

        self.answered_politicians.add(self.correct_politician)
        self.save()

        if self.is_game_ended():
            self.ended = django_now()
        else:
            self.first_politician, self.second_politician = PoliticianGame.generate_random_politician_pair(
                self.answered_politicians.all())
            self.correct_politician = random.choice([self.first_politician, self.second_politician])

        self.save()
        return self

    def polititian_cards(self):
        PoliticianCard = namedtuple("PoliticianCard", ["photo", "name", "url", "is_correct", "more_info"])
        base_url = reverse('seimas_politician_game')

        return [
            PoliticianCard(photo=self.first_politician.photo.url,
                           name=self.first_politician.name,
                           url=add_url_params(base_url, {'politician': self.first_politician.id}),
                           is_correct=self.first_politician.id == self.correct_politician.id,
                           more_info=self.first_politician.bio_url),
            PoliticianCard(photo=self.second_politician.photo.url,
                           name=self.second_politician.name,
                           url=add_url_params(base_url, {'politician': self.second_politician.id}),
                           is_correct=self.second_politician.id == self.correct_politician.id,
                           more_info=self.second_politician.bio_url),
        ]
