# Generated by Django 3.1.3 on 2023-08-11 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0043_auto_20230801_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='role',
            field=models.PositiveIntegerField(choices=[(1, 'Applicant'), (2, 'Admission Department'), (3, 'English Department'), (4, 'Scholarships Department'), (5, 'Supervisor Department'), (6, 'Admission Manager'), (7, 'Pharmacy Dean'), (8, 'Communication Department'), (9, 'Medicine Dean'), (10, 'Science Dean'), (11, 'Register Review'), (12, 'English Conformer'), (13, 'Interview Test'), (14, 'Equation Supervisor'), (15, 'Head Of Department'), (16, 'Registration'), (90, 'Super Admin')], unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveIntegerField(choices=[(1, 'Applicant'), (2, 'Admission Department'), (3, 'English Department'), (4, 'Scholarships Department'), (5, 'Supervisor Department'), (6, 'Admission Manager'), (7, 'Pharmacy Dean'), (8, 'Communication Department'), (9, 'Medicine Dean'), (10, 'Science Dean'), (11, 'Register Review'), (12, 'English Conformer'), (13, 'Interview Test'), (14, 'Equation Supervisor'), (15, 'Head Of Department'), (16, 'Registration'), (90, 'Super Admin')]),
        ),
    ]
