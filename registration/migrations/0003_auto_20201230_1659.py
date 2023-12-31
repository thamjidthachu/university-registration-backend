# Generated by Django 3.1.4 on 2020-12-30 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0002_auto_20201228_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicant',
            name='contact_result',
            field=models.CharField(blank=True, choices=[('WA', 'Will Attend'), ('NR', 'No Reply'), ('WR', 'Withdrew Registration'), ('MM', 'Major Medicine')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='online',
            field=models.BooleanField(default=True),
        ),
    ]

