# Generated by Django 3.1.3 on 2023-07-08 06:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0040_auto_20230707_1935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='englishtest',
            name='applicant_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='english_applicants', to='registration.applicant'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='applicant_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interview_applicants', to='registration.applicant'),
        ),
    ]