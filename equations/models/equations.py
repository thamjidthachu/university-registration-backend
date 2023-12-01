from django.db import models
from django.conf import settings
from registration.models.applicant import Applicant
from equations.models.courses import EquivalentCourse
from django.template.defaultfilters import slugify
from django.utils.timezone import now

STATUS_CHOICES = (
    ('UR', 'Under Review'),
    ('IA', 'Initial Acceptance'),
    ('AC', 'Accepted'),
    ('NM', 'Need Modification'),
    ('RJ', 'Rejected'),
)


def get_image_filename(instance, filename):
    slug = slugify(instance.applicant.application_no)
    return "applicant_%s/%s" % (slug, filename)


class Equation(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="equation_applicants")
    equation_courses = models.ManyToManyField(EquivalentCourse, blank=True)
    init_state = models.CharField(choices=STATUS_CHOICES, max_length=3, default='UR')
    head_of_department_state = models.CharField(choices=STATUS_CHOICES, max_length=3, null=True, blank=True)
    final_state = models.CharField(choices=STATUS_CHOICES, max_length=3, null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    equation_file = models.FileField(upload_to=get_image_filename, blank=True, null=True)
    created = models.DateTimeField(default=now)
    final_state_date = models.DateTimeField(blank=True, null=True)
    confirmed_date = models.DateTimeField(blank=True, null=True)
