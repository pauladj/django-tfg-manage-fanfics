# Generated by Django 2.2 on 2019-05-31 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0030_auto_20190528_1059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reading',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
