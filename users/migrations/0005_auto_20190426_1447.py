# Generated by Django 2.2 on 2019-04-26 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20190419_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(default='profiles/default.png', upload_to='profiles'),
        ),
    ]
