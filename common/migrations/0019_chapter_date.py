# Generated by Django 2.2 on 2019-05-25 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0018_auto_20190524_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='date',
            field=models.DateField(auto_now=True),
        ),
    ]
