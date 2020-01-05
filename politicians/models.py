from django.db import models
from django.db.models import Count, Sum
from utils.utils import file_extension, django_now
from django.utils.text import slugify
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from web.models import User
# Create your models here.


#Common fields that are shared among all models.
class CommonModel(models.Model):    
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, editable=False, related_name="+")
    # updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, editable=False, null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, editable=False)

    class Meta:
        abstract = True


class PoliticianQuerySet(models.QuerySet):
    pass

class ActivePoliticianManager(models.Manager):
    def get_queryset(self):
        return PoliticianQuerySet(self.model, using=self._db).filter(is_active=True)

class Politicians(CommonModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='politicians', limit_choices_to={'is_politician': True})
    first_name = models.CharField(max_length=50, verbose_name=_('Vardas'))
    last_name = models.CharField(max_length=150, verbose_name=_('Pavardė'))
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_male = models.BooleanField(default=False)
    asm_id = models.IntegerField(unique=True, blank=True, null=True, help_text="Asmens id is used internally in seimas web")
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=12, null=True, blank=True)
    personal_website = models.URLField(null=True, blank=True)

    @property
    def get_first_name(self):
        return User.first_name
    
    @property
    def get_last_name(slef):
        return User.last_name

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
    
    objects = PoliticianQuerySet.as_manager()
    active = ActivePoliticianManager()

    def save(self, *args, **kwargs):
        if not self.first_name:
            self.first_name = self.get_first_name
        if not self.last_name:
            self.first_name = self.get_last_name
        if not self.slug:
            self.slug = slugify(f'{self.first_name} {self.last_name}')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
   
    class Meta:
        verbose_name_plural = "Politicians"

class Experience(CommonModel):
    XP_TYPE = (
        ('pol', 'Politinė patirtis'),
        ('work', 'Darbinė patirtis'),
    )
    POL_POS_TYPES = (
        ('mp', 'Seimo narys(-ė)'),
        ('mep', 'EP narys(-ė)'),
        ('pm', 'Premjeras(-ė)'),
        ('min', 'Ministras(-ė)'),
        ('my', 'Meras(-ė)'),
        ('mmu', 'Savivaldybės tarybos narys(-ė)'),
        ('ot', 'Kita')
    )
    politician = models.ForeignKey(Politicians, on_delete=models.CASCADE, related_name='experience')
    type = models.CharField(max_length=4, choices=XP_TYPE, blank=True, null=True, verbose_name=_('Patirties tipas'))
    pol_position = models.CharField(max_length=4, choices=POL_POS_TYPES, verbose_name=_('Politinės preigos'))
    other_position = models.CharField(max_length=300, blank=True, null=True, verbose_name=_('Kitos pareigos'), help_text=_('Pildyti, kai yra nustatyta darbinės patirties tipas'))
    institution = models.CharField(max_length=300, blank=True, null=True, verbose_name=_('Institucija/Įmonė'))
    start_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, verbose_name=_('Termino pradžia'))
    end_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, verbose_name=_('Termino pabaiga'))


class Promises(CommonModel):
    STATUS_TYPES = (
        (1, "Nepradėtas"),
        (2, "Procese"),
        (3, "Užbaigtas")        
    )
    politician = models.ForeignKey(Politicians, on_delete=models.CASCADE, related_name='promises')
    promise_text = models.TextField(null=False, blank=False, verbose_name=_('Pažadas'))
    video_url = models.URLField(max_length=200, null=True, blank=True, verbose_name=_('Pažado įrašo nuoroda'))
    news_url = models.URLField(max_length=200, null=True, blank=True, verbose_name=_('Pažado įgyvendinimo įrodymai'))
    is_measurable = models.BooleanField(default=False, verbose_name=_('Ar pamatuojamas?'))
    status = models.SmallIntegerField(choices=STATUS_TYPES, null=True, blank=True, verbose_name=_('Būsena'))
    target = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Pažado tikslas'))
    target_initial_deadline = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, verbose_name=_('Pradinė tikslo įgyvendinimo data'))
    target_new_deadline = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, verbose_name=_('Nauja tikslo įgyvendinimo data'))
    end_target_value =  models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Galutinis tikslo rezultatas'))
    total_score = models.IntegerField(default=0, editable=False, verbose_name=_('Bendradarbiavimo balas'))
    experts_comments = models.TextField(null=True, blank=True, verbose_name=_('Eksperto komentaras'))
    cancellation_reason_text = models.TextField(null=True, blank=True, verbose_name=_('Pažado neįgyvendinimo priežastis'))
    commenst = models.TextField(null=True, blank=True, verbose_name=_('Komentarai'))

    def __str__(self):
        return self.promise_text

class PromiseAction(CommonModel):
    def _monitoring_attachments(self, filename):
        ext = file_extension(filename)
        date = django_now()
        filename = f"{filename}-attachment-{date}.{ext}"
        return join('attachments','politicians', filename)

    TYPES = (
        (1, "Išsiųstas laiškas"),
        (2, "Gautas laiškas"),
        (3, "Tipas 3")
    )
    promise = models.ForeignKey(Promises, on_delete=models.CASCADE, related_name='promise_action')
    action_text = models.CharField(max_length=200)
    action_type = models.SmallIntegerField(choices=TYPES, null=True, blank=True)
    attachment = models.FileField(upload_to=_monitoring_attachments, null=True, blank=True, verbose_name=_('Prisegtukas'))
    score = models.SmallIntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.action_text
