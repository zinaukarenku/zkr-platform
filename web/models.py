import uuid
from os.path import join
from typing import Optional

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField

from elections.models import MayorCandidate, PresidentCandidate, EuroParliamentCandidate
from seimas.models import Politician as SeimasPolitician
from utils.utils import distinct_by, file_extension, gravatar_url
from zkr import settings


class User(AbstractUser):
    def _user_photo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.get_full_name())

        filename = f"{slug}-photo.{ext}"
        return join('img', 'users', filename)

    photo = ResizedImageField(blank=True, null=True, upload_to=_user_photo_file,
                              crop=['middle', 'center'], size=[256, 256],
                              verbose_name=_("Nuotrauka"))

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)

    @cached_property
    def photo_url(self):
        if self.photo:
            return self.photo.url

        return gravatar_url(self.email, 200)

    @cached_property
    def all_social_accounts(self):
        return SocialAccount.objects.filter(user=self)

    def facebook_social_account(self):
        for social_account in self.all_social_accounts:
            if social_account.provider == 'facebook':
                return social_account

    def google_social_account(self):
        for social_account in self.all_social_accounts:
            if social_account.provider == 'google':
                return social_account

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name_plural = _("Registruoti vartotojai")
        verbose_name = _("Registruotas vartotojas")


class MunicipalityQuerySet(models.QuerySet):
    def annotate_with_organization_members_count(self):
        return self.annotate(organization_members_count=models.Count('organization_members'))


class Municipality(models.Model):
    name = models.CharField(max_length=256, db_index=True, verbose_name=_("Savivaldybės pavadinimas"))
    slug = models.SlugField(unique=True)

    objects = MunicipalityQuerySet.as_manager()

    class Meta:
        verbose_name_plural = _("Savivaldybės")
        verbose_name = _("Savivaldybė")
        ordering = ['slug']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class EmailSubscription(models.Model):
    email = models.EmailField(unique=True, verbose_name=_("El. paštas"))

    user_ip = models.GenericIPAddressField(verbose_name=_("IP adresas"))
    user_agent = models.TextField(blank=True, null=True)

    user_country = models.CharField(max_length=30, blank=True, null=True, verbose_name=_("Šalis"))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _("El. pašto prenumeratos")
        verbose_name = _("El. pašto prenumerata")

        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.email = self.email.strip().lower()
        super().save(force_insert, force_update, using, update_fields)


class OrganizationMemberGroup(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name=_("Komandos pavadinimas"))
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = _("Organizacijos narių komandos")
        verbose_name = _("Organizacijos narių komanda")
        ordering = ['order']

    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    def _organization_member_photo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.name)

        filename = f"{slug}-photo.{ext}"
        return join('img', 'zkr', 'member', filename)

    name = models.CharField(max_length=128, verbose_name=_("Vardas"))
    role = models.CharField(max_length=256, verbose_name=_("Nario rolė"), blank=True, null=True)

    photo = ResizedImageField(upload_to=_organization_member_photo_file, crop=['middle', 'center'], size=[256, 256],
                              verbose_name=_("Nuotrauka"))

    group = models.ForeignKey(
        OrganizationMemberGroup, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Veiklos grupė"),
        help_text=_("Jei vartotojas nėra priskiriamas, jokiai grupei jis bus rodomas tik regioninėse grupėse."),
        related_name="members",
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True,
                                related_name="organization_member", verbose_name=_("Registruotas vartotojas"),
                                help_text=_("Nustatyti šį laukelį, kad žmogus galėtų prisijungti prie admino"))
    municipalities = models.ManyToManyField(Municipality, blank=True, verbose_name=_("Savivaldybės"),
                                            help_text=_(
                                                "Nurodomos savivaldybės, kurioms priklauso organizacijos narys"))

    email = models.EmailField(blank=True, null=True, verbose_name=_("El. pašto adresas"))
    facebook_url = models.URLField(blank=True, null=True, verbose_name=_("Facebook"))
    twitter_url = models.URLField(blank=True, null=True, verbose_name=_("Twitter"))
    linkedin_url = models.URLField(blank=True, null=True, verbose_name=_("LinkedIn"))

    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = _("Organizacijos nariai")
        verbose_name = _("Organizacijos narys")
        ordering = ['order']
        default_related_name = 'organization_members'

    def __str__(self):
        return self.name


class OrganizationPartner(models.Model):
    def _organization_partner_logo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.name)

        filename = f"{slug}-photo.{ext}"
        return join('img', 'zkr', 'partners', filename)

    name = models.CharField(max_length=256, verbose_name=_("Pavadinimas"))
    logo = models.ImageField(upload_to=_organization_partner_logo_file, verbose_name=_("Logotipas"))
    url = models.URLField(verbose_name=_("Nuoroda į organizacijos puslapį"))
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = _("Organizacijos partneriai")
        verbose_name = _("Organizacijos partneris")
        ordering = ['order']

    def __str__(self):
        return self.name


class PoliticianInfoQuerySet(models.QuerySet):
    def annotate_with_promise_count(self):
        return self.annotate(promise_count=models.Count('promises'))


class ActivePoliticianInfoManager(models.Manager):
    def get_queryset(self):
        return PoliticianInfoQuerySet(self.model, using=self._db).filter(is_active=True)


class PoliticianInfo(models.Model):
    name = models.CharField(max_length=256, db_index=True, verbose_name=_("Politiko vardas"))
    is_active = models.BooleanField(db_index=True, verbose_name=_("Aktyvus"), default=True,
                                    help_text=_("Indikuoja ar politiko informacija aktyvi ir galima užduoti klausimą."))

    seimas_politician = models.OneToOneField(SeimasPolitician, on_delete=models.PROTECT, null=True, blank=True,
                                             related_name="politician_info",
                                             verbose_name=_("Seimo politiko profilis"),
                                             help_text=_("Sujungia seimo narį su politiku"))
    mayor_candidate = models.OneToOneField(MayorCandidate, on_delete=models.CASCADE, null=True, blank=True,
                                           related_name="politician_info",
                                           verbose_name=_("Kandidatas į merus"),
                                           help_text=_("Sujungia kandidatą į merus su politiku"))
    president_candidate = models.OneToOneField(PresidentCandidate, on_delete=models.CASCADE, null=True, blank=True,
                                            related_name="politician_info",
                                            verbose_name=_("Kandidatas į LR Prezidento postą"),
                                            help_text=_("Sujungti kandidatą į LR Prezidento postą su politiku"))

    authenticated_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        related_name="politician_infos",
        verbose_name=_("Vartotojai"),
        help_text=_(
            "Nustatyti vartotojai galės atsakinėti į klausimus skirtus politikui")
    )

    registration_secret_id = models.UUIDField(default=uuid.uuid4)

    email = models.EmailField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PoliticianInfoQuerySet.as_manager()
    active = ActivePoliticianInfoManager()

    @property
    def photo(self):
        if self.seimas_politician:
            return self.seimas_politician.photo
        if self.mayor_candidate:
            return self.mayor_candidate.photo
        if self.president_candidate:
            return self.president_candidate.photo

    def get_absolute_url(self):
        if self.seimas_politician is not None:
            return self.seimas_politician.profile_url
        if self.mayor_candidate is not None:
            return self.mayor_candidate.profile_url
        if self.president_candidate is not None:
            return self.president_candidate.profile_url

    @property
    def short_description(self) -> Optional[str]:
        if self.seimas_politician:
            return self.seimas_politician.fraction_name
        if self.mayor_candidate:
            return f"Kandidatas į merus {self.mayor_candidate.municipality.name}"
        if self.president_candidate:
            return f"Kandidatas į LR Prezidentus"

    @property
    def contact_emails(self):
        emails = []
        if hasattr(self, 'seimas_politician') and self.seimas_politician:
            seimas_politician = self.seimas_politician

            if seimas_politician.email:
                emails.append(seimas_politician.email)

        if hasattr(self, 'mayor_candidate') and self.mayor_candidate:
            mayor_candidate = self.mayor_candidate

            if mayor_candidate.email:
                emails.append(mayor_candidate.email)

        if self.email:
            emails.append(self.email)

        for user in self.authenticated_users.all():
            emails.append(user.email)

        return distinct_by(emails)

    class Meta:
        verbose_name_plural = _("Politikų informacija")
        verbose_name = _("Politiko informacija")
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name


class PoliticianPromise(models.Model):
    politician = models.ForeignKey(PoliticianInfo, on_delete=models.CASCADE, verbose_name=_("Politikas"))
    debates = models.ForeignKey("elections.Debates", on_delete=models.CASCADE, verbose_name=_("Debatai"))
    promise = models.TextField(verbose_name=_("Politiko pažadas"))
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _("Politikų pažadai")
        verbose_name = _("Politiko pažadas")
        ordering = ["order"]
        default_related_name = "promises"

    def __str__(self):
        return self.promise

