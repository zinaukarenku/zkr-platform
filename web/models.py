from os.path import join

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify
from django_resized import ResizedImageField

from zkr.utils import file_extension
from zkr import settings


class User(AbstractUser):
    photo = models.ImageField(blank=True, null=True, upload_to='img/users/')

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)

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


class EmailSubscription(models.Model):
    email = models.EmailField(unique=True)

    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "E-mail subscriptions"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.email = self.email.strip().lower()
        super().save(force_insert, force_update, using, update_fields)


class OrganizationMemberGroup(models.Model):
    name = models.CharField(max_length=128, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Organization member groups"
        ordering = ['order']

    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    def _organization_member_photo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.name)

        filename = f"{slug}-photo.{ext}"
        return join('img', 'zkr', 'member', filename)

    name = models.CharField(max_length=128)
    role = models.CharField(max_length=256)

    photo = ResizedImageField(upload_to=_organization_member_photo_file, crop=['middle', 'center'], size=[256, 256])

    group = models.ForeignKey(OrganizationMemberGroup, on_delete=models.CASCADE, related_name="members")

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True,
                                related_name="organization_member")

    email = models.EmailField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Organization members"
        ordering = ['order']

    def __str__(self):
        return self.name


class OrganizationPartner(models.Model):
    def _organization_partner_logo_file(self, filename):
        ext = file_extension(filename)
        slug = slugify(self.name)

        filename = f"{slug}-photo.{ext}"
        return join('img', 'zkr', 'partners', filename)

    name = models.CharField(max_length=256)
    logo = models.ImageField(upload_to=_organization_partner_logo_file)
    url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Organization partners"
        ordering = ['order']

    def __str__(self):
        return self.name
