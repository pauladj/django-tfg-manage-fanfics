# Generated by Django 2.2 on 2019-05-18 18:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_auto_20190518_1637'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fanfic',
            name='num_chapters',
        ),
        migrations.RemoveField(
            model_name='fanfic',
            name='status',
        ),
    ]
