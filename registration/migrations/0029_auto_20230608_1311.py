# Generated by Django 3.1.3 on 2023-06-08 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0028_auto_20230512_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicant',
            name='english_certf_result',
            field=models.CharField(blank=True, choices=[('V', 'Verified'), ('E', 'Expired'), ('UN', 'Unknown'), ('U', 'Unknown Certificate')], max_length=3, null=True),
        ),
    ]
