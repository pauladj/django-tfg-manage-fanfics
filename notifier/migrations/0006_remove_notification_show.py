# Generated by Django 2.0 on 2019-04-01 18:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifier', '0005_notification_show'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='show',
        ),
    ]
