# Generated by Django 2.0 on 2019-03-31 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifier', '0004_auto_20190331_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='show',
            field=models.BooleanField(default=False),
        ),
    ]