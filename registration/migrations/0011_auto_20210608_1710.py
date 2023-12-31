# Generated by Django 3.2 on 2021-06-08 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0010_auto_20210422_1920'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.PositiveIntegerField(choices=[(1, 'Applicant'), (2, 'Admission Department'), (3, 'English Department'), (4, 'Scholarships Department'), (5, 'Supervisor Department'), (6, 'Admission Manager'), (7, 'Pharmacy Dean'), (8, 'Communication Department'), (9, 'Medicine Dean'), (10, 'Science Dean'), (11, 'Register Review'), (12, 'English Confirmer'), (13, 'Interview Test'), (14, 'Equation Supervisor'), (90, 'Super Admin')], unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='applicant',
            name='arabic_speaker',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='user_major',
            field=models.CharField(blank=True, choices=[('MS', 'Medicine & Surgery'), ('PHD', 'Pharm D'), ('NU', 'Nursing'), ('RT', 'Respiratory Therapy'), ('EMS', 'Emergency Medical Services'), ('AT', 'Anaesthesia Technology'), ('HIS', 'Health Information Systems'), ('IS', 'Information Systems'), ('CS', 'Computer Science'), ('IE', 'Industrial Engineering'), ('GSE', 'General science & English'), ('NM', 'No Major')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='state_university',
            field=models.CharField(blank=True, choices=[('RE', 'Regular'), ('OU', 'Outgoing'), ('AP', 'Apologize'), ('PP', 'Postponed'), ('AS', 'Academically_separated'), ('DD', 'Disciplinary_disconnected'), ('FR', 'Folded_registration'), ('GR', 'Graduated')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveIntegerField(choices=[(1, 'Applicant'), (2, 'Admission Department'), (3, 'English Department'), (4, 'Scholarships Department'), (5, 'Supervisor Department'), (6, 'Admission Manager'), (7, 'Pharmacy Dean'), (8, 'Communication Department'), (9, 'Medicine Dean'), (10, 'Science Dean'), (11, 'Register Review'), (12, 'English Confirmer'), (13, 'Interview Test'), (14, 'Equation Supervisor'), (90, 'Super Admin')]),
        ),
        migrations.AddField(
            model_name='user',
            name='user_roles',
            field=models.ManyToManyField(blank=True, to='registration.Role'),
        ),
    ]
