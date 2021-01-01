# Generated by Django 2.2 on 2019-04-27 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20190427_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='privacy',
            field=models.IntegerField(choices=[(1, 'following'), (2, 'all'), (3, 'nobody')], default=2),
        ),
    ]
