# Generated by Django 3.2 on 2021-06-13 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0012_alter_user_user_major'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='faculty',
            field=models.CharField(choices=[('M', 'Medicine'), ('PH', 'Pharmacy'), ('AS', 'Applied Science'), ('ALL', 'All Faculties')], default='ALL', max_length=10),
        ),
    ]
