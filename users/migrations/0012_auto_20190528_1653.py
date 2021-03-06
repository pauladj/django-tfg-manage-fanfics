# Generated by Django 2.2 on 2019-05-28 16:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20190515_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='following',
            name='user_one',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_one_following', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='following',
            name='user_two',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_two_following', to=settings.AUTH_USER_MODEL),
        ),
    ]
