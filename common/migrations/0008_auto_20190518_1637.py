# Generated by Django 2.2 on 2019-05-18 16:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_auto_20190518_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='fanfic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Fanfic'),
        ),
        migrations.AlterUniqueTogether(
            name='chapter',
            unique_together={('num_chapter', 'fanfic')},
        ),
    ]
