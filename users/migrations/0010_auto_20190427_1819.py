# Generated by Django 2.2 on 2019-04-27 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_following'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='gender',
            field=models.CharField(blank=True, choices=[('m', 'Male'), ('f', 'Female')], max_length=1, null=True),
        ),
    ]