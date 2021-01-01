# Generated by Django 2.2 on 2019-05-27 12:24

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0020_delete_privatemessage'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='characterfanfic',
            unique_together={('character', 'fanfic')},
        ),
        migrations.AlterUniqueTogether(
            name='fandomfanfic',
            unique_together={('fandom', 'fanfic')},
        ),
        migrations.AlterUniqueTogether(
            name='pairing',
            unique_together={('fanfic', 'character_one', 'character_two')},
        ),
        migrations.AlterUniqueTogether(
            name='reading',
            unique_together={('chapter', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('user', 'fanfic')},
        ),
    ]
