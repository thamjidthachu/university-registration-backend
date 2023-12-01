from django.db import models
from django.conf import settings
from registration.models.lookup import University

FACULTY = (
    (1, "Medicine"),
    (2, "Pharmacy"),
    (3, "Applied Science"),
)


class UniversirtyCourse(models.Model):
    objects = None
    name = models.CharField(max_length=75)
    course_no = models.IntegerField(unique=True)
    arabic_name = models.CharField(max_length=75)
    code = models.CharField(max_length=20)
    arabic_code = models.CharField(max_length=20)
    hours = models.SmallIntegerField()
    faculty = models.SmallIntegerField(choices=FACULTY)

    class Meta:
        verbose_name = "University Course"
        verbose_name_plural = "University Courses"

    def __str__(self):
        return self.name


class EquivalentCourse(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    equivalent_to = models.ForeignKey(UniversirtyCourse, on_delete=models.CASCADE)
    name = models.CharField(max_length=75)
    code = models.CharField(max_length=20)
    hours = models.SmallIntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exception = models.BooleanField(default=False)

    def __str__(self):
        return self.name
