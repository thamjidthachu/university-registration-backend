from django.db import models


class TokenList(models.Model):
    user = models.IntegerField()
    full_name = models.CharField(max_length=2500)
    user_type = models.CharField(max_length=50)
    token = models.CharField(max_length=300, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField(blank=True, null=True)
