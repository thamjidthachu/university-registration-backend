from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify

from .applicant import Applicant, Reservation

# Implemented By Mohamed samy.

ENG_TEST_TYPES = (
    ('T', 'TOEFL'),
    ('I', 'IELTS'),
    ('OX', 'Oxford'),
    ('S', 'Step'),
)
RES_CHOICES = (
    ('AT', 'Attended'),
    ('S', 'Succeeded'),
    ('F', 'Failed'),
    ('P', 'Postponed'),
    ('A', 'Absent'),
    ('L', 'Low Score'),
    ('U', 'Unknown Certificate'),
)


def get_image_filename(instance, filename):
    slug = slugify(instance.applicant_id.application_no)
    return "applicant_%s/%s" % (slug, filename)


class Interview(models.Model):
    applicant_id = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='interview_applicants')
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    date_modified = models.DateTimeField(blank=True, null=True)
    outlook = models.CharField(blank=True, null=True, max_length=100)
    personality = models.CharField(blank=True, null=True, max_length=100)
    interest = models.CharField(blank=True, null=True, max_length=100)
    knowledge = models.CharField(blank=True, null=True, max_length=100)
    fitness = models.CharField(blank=True, null=True, max_length=100)
    english = models.CharField(blank=True, null=True, max_length=100)
    comment = models.TextField(blank=True, null=True)
    result = models.CharField(choices=RES_CHOICES, blank=True, null=True, max_length=50)
    university_certificate = models.FileField(upload_to=get_image_filename, blank=True, null=True)

    def __str__(self):
        return self.applicant_id.full_name


class EnglishTest(models.Model):
    TRY = (
        (1, "First Test"),
        (2, "Second Test"),
        (3, "Third Test")
    )
    applicant_id = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='english_applicants')
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    entry_user = models.CharField(max_length=100, blank=True, null=True)
    modify_user = models.DateTimeField(blank=True, null=True)
    test_type = models.CharField(choices=ENG_TEST_TYPES, blank=True, null=True, max_length=50)
    score = models.FloatField(blank=True, null=True)
    result = models.CharField(choices=RES_CHOICES, blank=True, null=True, max_length=50)
    test_try = models.SmallIntegerField(choices=TRY)
    original_certificate = models.FileField(upload_to=get_image_filename, blank=True, null=True)
    university_certificate = models.FileField(upload_to=get_image_filename, blank=True, null=True)
    notes = models.CharField(max_length=500, null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.applicant_id.full_name


class Absent(models.Model):
    applicant_id = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    def __str__(self):
        return self.applicant_id.full_name
