from django.db import models


class University(models.Model):
    university_code = models.IntegerField(blank=True, null=True)
    university_name_english = models.CharField(max_length=300, blank=True, null=True)
    university_name_arabic = models.CharField(max_length=300, blank=True, null=True)
    country_code = models.IntegerField(blank=True, null=True)
    university_type = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "university"
        verbose_name = "University"
        verbose_name_plural = "Universities"

    def __str__(self):
        return self.university_name_arabic
