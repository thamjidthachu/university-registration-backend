# Generated by Django 3.1.3 on 2023-06-13 11:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0034_auto_20230613_0926'),
    ]

    operations = [
        migrations.AddField(
            model_name='univpayments',
            name='Trans_code',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='univpayments',
            name='code',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pay_amount', to='registration.univpayments'),
        ),
    ]
