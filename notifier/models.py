import re
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

user_model = getattr(settings, "AUTH_USER_MODEL", User)


class Notification(models.Model):
    subject_user = models.ForeignKey(
        user_model, on_delete=models.CASCADE, null=True, blank=True,
        related_name="subject_user")

    # Generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    subject = GenericForeignKey(
        'content_type', 'object_id')
    verb = models.CharField(max_length=255)
    target = models.ForeignKey(user_model, on_delete=models.CASCADE)

    link = models.CharField(max_length=255, null=True, blank=True)
    read = models.BooleanField(default=False)  # read with button
    seen = models.BooleanField(default=False)  # seen in bubble
    when = models.DateTimeField(auto_now_add=True)
    in_feed = models.BooleanField(default=False)
    in_top_bar = models.BooleanField(default=False)
    reverse = models.BooleanField(default=False)

    @staticmethod
    def top_bar_notifications(user):
        """ Get the last notifications """
        notifications = Notification.objects.filter(
            target=user, in_top_bar=True).order_by('-when')[:15]
        return notifications

    @staticmethod
    def get_unseen_count(user):
        """ Get the unseen notification count of user """
        return Notification.objects.filter(target=user, read=False,
                                           seen=False, in_top_bar=True).count()

    def get_date(self):
        """ Get the date to show. If it's in the day show hours, if not
            show the date
         """
        date = ""

        hour = self.when.strftime("%H")
        month = str(self.when.month)
        minute = self.when.strftime("%M")
        year = self.when.strftime("%Y")
        day = self.when.strftime("%d")

        time = hour + ":" + minute

        if self.when.date() == datetime.today().date():
            # today
            date += "Today at " + time
        elif self.when.date() == datetime.today().date() - timedelta(1):
            # yesterday
            date += "Yesterday at " + time
        elif self.when.year == datetime.today().year:
            # not today but same year
            date += month + "/" + day + ", " + time
        else:
            # before this year
            date += (year + "/" + month + "/" +
                     day + ", " + time)
        return date

    def get_representative_image(self):
        """ Get the representative image of the notification """
        if hasattr(self.subject, 'get_image'):
            image = self.subject.get_image()
            if image is not None:
                return image
