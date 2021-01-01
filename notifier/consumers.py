# chat/consumers.py
from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from notifier.models import Notification
from common.models import Fanfic
from users.models import CustomUser
from django.db import transaction

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.user = self.scope["user"]
        self.group_name = "notifier_" + str(self.user.id)
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name)

    def message_new(self, event):
        self.send(text_data=event["text"])

    def receive(self, text_data):
        try:
            with transaction.atomic():
                text_data_json = json.loads(text_data)
                action = text_data_json['action']
                if action == "mark_as_read":
                    notification_id = text_data_json['notificationid']

                    notify_obj = Notification.objects.filter(
                        target=self.user, id=notification_id)
                    if notify_obj:
                        notify_obj = notify_obj.first()
                        notify_obj.read = True
                        notify_obj.seen = True
                        notify_obj.save()

                        if notify_obj.read is False:
                            raise Exception("Notification status could not "
                                            "be changed.")
                    else:
                        raise Exception("This notification does not "
                                        "exist anymore.")
                    text_data = json.dumps({
                        'action': "mark_as_read",
                        'notificationid': notification_id,
                    })

                    self.send_data(text_data)

                elif action == "mark_all_as_read":
                    Notification.objects.filter(
                        target=self.user, read=False).update(read=True,
                                                             seen=True)

                    text_data = json.dumps({
                        'action': "mark_all_as_read",
                        'message': "success"
                    })

                    self.send_data(text_data)
                elif action == "mark_all_as_seen":
                    Notification.objects.filter(
                        target=self.user).update(seen=True)

                    text_data = json.dumps({
                        'action': "mark_all_as_seen",
                        'message': "success"
                    })

                    self.send_data(text_data)
        except Exception as e:
            logger.error(e)

            text_data = json.dumps({
                'action': 'error',
                'message': str(e)
            })
            self.send_data(text_data)

    def send_data(self, text_data):
        group_name = "notifier_" + str(self.user.id)

        async_to_sync(self.channel_layer.group_send)(
            group_name,
            {
                "type": "message.new",
                "text": text_data,
            },
        )
