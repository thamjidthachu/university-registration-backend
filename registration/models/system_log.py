from django.db import models


class SystemLog(models.Model):

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    role = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    modified_to = models.CharField(max_length=150)
    date_modified = models.DateTimeField()
    modified_in = models.TextField()
    before_modified = models.TextField()

    def __str__(self):
        return self.full_name

