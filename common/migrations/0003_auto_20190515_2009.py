# Generated by Django 2.2 on 2019-05-15 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_fandomfanfic_is_primary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.FloatField(default=0),
        ),
    ]
