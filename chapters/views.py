import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from common.models import Reading, Chapter, Fanfic
from common.utils import CustomError
from common.views import BaseView
# Get an instance of a logger
from notifier.models import Notification

# Create your views here.

logger = logging.getLogger(__name__)


class ChaptersNotesView(LoginRequiredMixin, BaseView):
    def delete(self, request, fanfic_id=None):
        """ Clear private notes of user for one fanfic"""
        if fanfic_id is None:
            raise PermissionDenied()

        try:
            with transaction.atomic():
                fanfic = get_object_or_404(Fanfic, id=fanfic_id)

                Reading.objects.filter(chapter__fanfic=fanfic,
                                       user=request.user).update(
                    private_notes=None)

                message = "The private notes have been successfully deleted"
                messages.success(request, message)
                logger.info(message)
        except Exception as e:
            logger.error("Error deleting private notes {}".format(e))
            message = "There was an unexpected error trying to delete the " \
                      "private notes."
            messages.error(request, message)

        return redirect(fanfic.get_url())

    def post(self, request, fanfic_id=None, chapter_id=None):
        """ Create/edit message"""
        if fanfic_id is None or chapter_id is None or request.is_ajax() is \
                False:
            raise PermissionDenied()

        try:
            with transaction.atomic():
                chapter = get_object_or_404(Chapter, id=chapter_id)

                if chapter.fanfic.id != int(fanfic_id):
                    raise PermissionDenied

                text = request.POST.get("text")

                if not text or len(text) == 0 or len(
                        text.replace(" ", "")) == 0:
                    # text is empty
                    text = None
                elif text and len(text) > 200:
                    raise CustomError("The text cannot have more than 200 "
                                      "characters.")

                readings = Reading.objects.filter(chapter=chapter,
                                                  user=request.user)
                if readings.exists():
                    # it already exists, update content
                    user_reading = readings.first()
                    if text is None and user_reading.read is False:
                        user_reading.delete()
                    else:
                        user_reading.private_notes = text
                        user_reading.save()
                else:
                    # create new reading
                    Reading.objects.create(chapter=chapter,
                                           user=request.user,
                                           private_notes=text)

                success = True
                message = "The private note has been saved"
        except CustomError as e:
            logger.error("Error saving private notes {}".format(e))
            success = False
            message = str(e)
        except Exception as e:
            logger.error("Error saving private notes {}".format(e))
            success = False
            message = "There was an unexpected error trying to update the " \
                      "private note."

        # return json
        data = {
            "success": success,
            "message": message,
        }
        return HttpResponse(json.dumps(data), content_type='text/plain',
                            status=200)


class ChaptersView(LoginRequiredMixin, BaseView):
    def delete(self, request, fanfic_id=None):
        """ Clear all the data of one user for one fanfic"""
        if fanfic_id is None:
            raise PermissionDenied()

        try:
            with transaction.atomic():
                fanfic = get_object_or_404(Fanfic, id=fanfic_id)

                Reading.objects.filter(chapter__fanfic=fanfic,
                                       user=request.user).delete()

                message = "All the data has been successfully deleted"
                logger.info(message)
                messages.success(request, message)
        except Exception as e:
            logger.error("Error deleting the chapters data {}".format(e))
            message = "There was an unexpected error trying to delete the " \
                      "user data."
            messages.error(request, message)

        return redirect(fanfic.get_url())

    def post(self, request, fanfic_id=None):
        """ Mark all chapters as read """
        if fanfic_id is None:
            raise PermissionDenied()

        try:
            with transaction.atomic():
                fanfic = get_object_or_404(Fanfic, id=fanfic_id)

                fanfic_chapters = Chapter.objects.filter(
                    fanfic=fanfic)
                for chapter in fanfic_chapters:
                    reading = Reading.objects.filter(chapter=chapter,
                                                     user=request.user)
                    if reading.exists():
                        reading_obj = reading.first()
                        reading_obj.read = True
                        reading_obj.save()
                    else:
                        # create reading obj
                        Reading.objects.create(user=request.user,
                                               chapter=chapter, read=True)

                message = "All the chapters have been marked as read."
                messages.success(request, message)
        except Exception as e:
            logger.error("Error marking all chapters as read {}".format(e))
            message = "There was an unexpected error trying to mark the " \
                      "chapters as read."
            messages.error(request, message)

        return redirect(fanfic.get_url())


class ChaptersMarkAsReadView(LoginRequiredMixin, BaseView):
    def post(self, request, fanfic_id=None, chapter_id=None):
        """ Mark chapter as read/unread """
        if fanfic_id is None or chapter_id is None or request.is_ajax() is \
                False:
            raise PermissionDenied()

        try:
            with transaction.atomic():
                chapter = get_object_or_404(Chapter, id=chapter_id)
                if chapter.fanfic.id != int(fanfic_id):
                    raise PermissionDenied

                reading = Reading.objects.filter(user=request.user,
                                                 chapter=chapter)

                notification = False
                if reading.exists():
                    reading = reading.first()
                    status = reading.read

                    if status is True and reading.private_notes is None:
                        reading.delete()
                    else:
                        reading.read = True if status is False else False
                        reading.save()

                        if status is False:
                            notification = True
                else:
                    Reading.objects.create(user=request.user,
                                           chapter=chapter,
                                           read=True)
                    notification = True

                if notification is True:
                    # create notification
                    Notification.objects.create(
                        subject=chapter.fanfic, verb="has read chapter {} "
                                                     "of".format(
                            chapter.num_chapter),
                        target=request.user,
                        reverse=True,
                        link=chapter.fanfic.get_url(),
                        in_top_bar=False, in_feed=True)

                success = True
                message = "The chapter has been updated."
        except Exception as e:
            logger.error("Error marking a chapter as read/unread {}".format(e))
            success = False
            message = "There was an unexpected error trying to update the " \
                      "chapter status."

        # return json
        data = {
            "success": success,
            "message": message,
            "checked": notification
        }
        return HttpResponse(json.dumps(data), content_type='text/plain',
                            status=200)


class ChaptersMarkAsReadLastView(LoginRequiredMixin, BaseView):
    def post(self, request, fanfic_id=None):
        """ Mark chapter as read last chapter of a fanfic """
        if fanfic_id is None or request.is_ajax() is \
                False:
            raise PermissionDenied()

        notification = False
        more_chapters = None
        chapters_read_count = None
        total_count = None
        success = False
        message = None
        chapter_marked_as_read = None
        try:
            with transaction.atomic():
                fanfic = get_object_or_404(Fanfic, id=fanfic_id)

                read_chapters = Reading.objects.filter(
                    chapter__fanfic=fanfic, read=True,
                    user=request.user).values_list(
                    'chapter__id', flat=True)
                unread_chapters = Chapter.objects.exclude(
                    id__in=read_chapters).filter(
                    fanfic=fanfic).order_by('num_chapter')
                if unread_chapters.exists():
                    one_unread_chapter = unread_chapters.first()
                    reading_user = Reading.objects.filter(
                        chapter=one_unread_chapter, user=request.user,
                        read=False)
                    if reading_user.exists() is False:
                        Reading.objects.create(user=request.user,
                                               chapter=one_unread_chapter,
                                               read=True)
                    else:
                        reading_user = reading_user.first()
                        reading_user.read = True
                        reading_user.save()
                    chapter_marked_as_read = one_unread_chapter
                    message = "The chapter has been marked as read."
                    notification = True

                else:
                    message = "There are no more chapters to read for " \
                              "this fanfic."

                if notification is True:
                    # create notification
                    Notification.objects.create(
                        subject=chapter_marked_as_read.fanfic,
                        verb="has read chapter {} "
                             "of".format(
                            chapter_marked_as_read.num_chapter),
                        target=request.user,
                        reverse=True,
                        link=chapter_marked_as_read.fanfic.get_url(),
                        in_top_bar=False, in_feed=True)

                total_count = Chapter.objects.filter(fanfic=fanfic).count()
                chapters_read_count = Reading.objects.filter(
                    chapter__fanfic=fanfic, user=request.user).count()
                if total_count == chapters_read_count:
                    more_chapters = False
                else:
                    more_chapters = True

                success = True

        except Exception as e:
            logger.error("Error marking a chapter as read {}".format(e))
            success = False
            message = "There was an unexpected error trying to update the " \
                      "chapter status."

        # return json
        json_response = {
            'moreChapters': more_chapters,
            'totalCount': total_count,
            'chaptersReadCount': chapters_read_count,
            'success': success,
            'message': message
        }
        return HttpResponse(json.dumps(json_response),
                            content_type='text/plain',
                            status=200)
