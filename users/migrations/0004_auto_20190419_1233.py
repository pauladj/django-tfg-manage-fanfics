# Generated by Django 2.2 on 2019-04-19 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20190401_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='about_me',
            field=models.TextField(blank=True, null=True, verbose_name='about me'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='gender',
            field=models.CharField(blank=True, choices=[('m', 'male'), ('f', 'female')], max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='website',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='my website'),
        ),
    ]
