# Generated by Django 2.2 on 2019-05-28 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0029_auto_20190528_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submittedreport',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
