# Generated by Django 3.1.3 on 2021-11-17 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equations', '0006_auto_20211025_0206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equation',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='equivalentcourse',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='service',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='universirtycourse',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]