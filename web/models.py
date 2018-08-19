from os.path import join

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django_resized import ResizedImageField

from seimas.utils import file_extension


class User(AbstractUser):
    pass


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
    photo = ResizedImageField(upload_to=_organization_member_photo_file, crop=['middle', 'center'], size=[256, 256])

    group = models.ForeignKey(OrganizationMemberGroup, on_delete=models.CASCADE, related_name="members")
    role = models.CharField(max_length=256)

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
    logo = models.ImageField()
    url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Organization partners"
        ordering = ['order']

    def __str__(self):
        return self.name
