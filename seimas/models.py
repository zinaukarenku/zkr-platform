from django.db import models


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


class Party(models.Model):
    name = models.CharField(max_length=50, unique=True)

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


class Politician(models.Model):
    asm_id = models.IntegerField(unique=True, help_text="Asmens id is used internally in seimas web")

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_male = models.BooleanField(default=True)

    elected_party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="politicians")

    start = models.DateField()
    end = models.DateField(blank=True, null=True)

    bio_url = models.URLField(null=True, blank=True)

    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=12, null=True, blank=True)
    personal_website = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Politicians"

    def __str__(self):
        return self.name


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

    is_secondment = models.BooleanField(default=False, verbose_name="True stands for Komandiruotė, False for Kelionė")

    class Meta:
        verbose_name_plural = "Politician business trips"
        ordering = ['politician', '-start']
        unique_together = ['politician', 'name']

    def __str__(self):
        return f"{self.politician} business trip {self.name}"

# class PoliticianTerm(models.Model):
#     politician = models.ForeignKey(Politician, on_delete=models.CASCADE)
#     term = models.ForeignKey(Term, on_delete=models.CASCADE)
#
#     class Meta:
#         verbose_name_plural = "Politicians"
#         ordering = ['politician', 'term']
#         unique_together = ['politician', 'term']
#
#     def __str__(self):
#         return f"{self.politician} {self.term}"
