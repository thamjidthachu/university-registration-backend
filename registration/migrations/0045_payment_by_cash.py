# Generated by Django 3.1.3 on 2023-08-11 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0044_auto_20230811_0751'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='by_cash',
            field=models.BooleanField(default=False),
        ),
    ]
