# Generated by Django 3.1.3 on 2021-01-06 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0005_auto_20210105_1740'),
    ]

    operations = [
        migrations.CreateModel(
            name='Absent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applicant_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.applicant')),
                ('reservation_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.reservation')),
            ],
        ),
    ]
