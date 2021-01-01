from django.db.models.signals import post_delete

from common.models import Fandom, FandomFanfic, Fanfic


def change_primary_fandom(sender, instance, using, **kwargs):
    """ Fanfics always have at least one fandom """
    with_primary_ids_fanfics = list(FandomFanfic.objects.filter(
        is_primary=True).values_list('fanfic__id', flat=True))
    without_primary = FandomFanfic.objects.exclude(
        fanfic__id__in=with_primary_ids_fanfics)

    without_primary_ids = list(without_primary.values_list('fanfic__id',
                                                           flat=True))
    without_primary.update(is_primary=True)

    existing_fanfics_ids = list(with_primary_ids_fanfics + without_primary_ids)

    non_existing_fanfics_ids = Fanfic.objects.exclude(
        id__in=existing_fanfics_ids)

    other_fandom = Fandom.objects.filter(name="Other",
                                         type__name="other").first()

    for fanfic in non_existing_fanfics_ids:
        FandomFanfic.objects.create(fandom=other_fandom, fanfic=fanfic,
                                    is_primary=True)


post_delete.connect(change_primary_fandom,
                    sender=Fandom)
