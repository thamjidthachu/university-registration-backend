# Generated by Django 3.1.3 on 2021-01-27 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0007_major_status_m'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicant',
            name='final_state_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]