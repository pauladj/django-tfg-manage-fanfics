# Generated by Django 2.2 on 2019-05-16 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifier', '0008_notification_subject_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='reverse',
            field=models.BooleanField(default=False),
        ),
    ]
