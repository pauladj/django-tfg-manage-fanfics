from django.db.models import Q
from django.db.models.signals import post_delete

from common.models import CharacterFanfic, Pairing


def delete_pairings(sender, instance, using, **kwargs):
    Pairing.objects.filter(fanfic__id=instance.fanfic.id).filter(Q(
        character_one__id=instance.character.id) | Q(
        character_two__id=instance.character.id)).delete()


post_delete.connect(delete_pairings,
                    sender=CharacterFanfic)
