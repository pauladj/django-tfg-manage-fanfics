import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save

from notifier.models import Notification

channel_layer = get_channel_layer()


def send_new_notification_to_user(sender, instance, created, **kwargs):
    if created is True and instance.in_top_bar is True:
        target_user = instance.target

        # send notification to user group
        group_name = "notifier_" + str(target_user.id)
        text = {"action": "new_notification",
                "link": instance.link,
                "read": instance.read,
                "notificationid": instance.id,
                "reverse": instance.reverse,
                "subject": str(instance.subject),
                "verb": instance.verb,
                "target": str(target_user),
                "image": instance.get_representative_image(),
                "date": instance.get_date()}

        async_to_sync(channel_layer.group_send)(
            group_name, {
                "type": "message.new",
                "text": json.dumps(text)
            }
        )


post_save.connect(send_new_notification_to_user,
                  sender=Notification)
