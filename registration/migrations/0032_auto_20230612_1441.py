# Generated by Django 3.1.3 on 2023-06-12 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0031_auto_20230612_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='englishtest',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='englishtest',
            name='result',
            field=models.CharField(blank=True, choices=[('AT', 'Attended'), ('S', 'Succeeded'), ('F', 'Failed'), ('P', 'Postponed'), ('A', 'Absent'), ('L', 'Low Score'), ('U', 'Unknown Certificate')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='interview',
            name='result',
            field=models.CharField(blank=True, choices=[('AT', 'Attended'), ('S', 'Succeeded'), ('F', 'Failed'), ('P', 'Postponed'), ('A', 'Absent'), ('L', 'Low Score'), ('U', 'Unknown Certificate')], max_length=50, null=True),
        ),
    ]
