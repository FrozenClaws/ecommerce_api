# Generated by Django 5.2.3 on 2025-06-27 04:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_alter_cartitem_rate_alter_cartitem_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discount',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0, message='Age cannot be negative.'), django.core.validators.MaxValueValidator(120, message='Age cannot exceed 120.')]),
        ),
    ]
