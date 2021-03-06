# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-02-10 13:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opencabs', '0025_booking_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('POA', 'Pay on arrival'), ('ONL', 'Online'), ('DPT', 'Department')], default='', max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('0', 'Request'), ('1', 'Confirmed'), ('2', 'Declined'), ('3', 'Attempt')], default='0', max_length=1),
        ),
    ]