# Generated by Django 3.1.3 on 2020-11-28 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tokens', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokenlist',
            name='expire_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
