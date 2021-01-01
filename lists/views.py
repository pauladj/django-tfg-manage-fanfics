import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from common.models import List, Fanfic, FanficList
from common.utils import CustomError
from common.views import BaseView
from notifier.models import Notification

logger = logging.getLogger(__name__)


class ListsView(LoginRequiredMixin, BaseView):
    def post(self, request, list_id=None):
        if request.is_ajax() is False or list_id is None:
            raise PermissionDenied()

        success = False
        message = "There was an unexpected error trying to process this " \
                  "action."
        try:
            with transaction.atomic():
                act_user = request.user
                list_user = List.objects.filter(user=act_user, id=list_id)
                if list_user.exists() is False:
                    raise CustomError("This list does not exist anymore.")

                list_user = list_user.first()

                fanfic_id = int(request.POST.get('fanficId'))
                mark_to_join = request.POST.get('join')
                mark_to_join = True if mark_to_join == 'true' else False

                fanfic = Fanfic.objects.filter(id=fanfic_id)
                if fanfic.exists() is False:
                    raise CustomError("This fanfic does not exist anymore.")

                fanfic = fanfic.first()

                fl = FanficList.objects.filter(list=list_user, fanfic=fanfic)
                if fl.exists() is True and mark_to_join is True:
                    # already added
                    success = True
                    message = "This fanfic has been already added to this " \
                              "list."
                    list_name = list_user.name
                    list_id_checked = list_user.id
                elif fl.exists() is True and mark_to_join is False:
                    # the user wants to remove the fanfic from this list
                    fl.delete()
                    success = True
                    message = "This fanfic is not on your lists anymore."

                    list_name = None
                    list_id_checked = None
                elif fl.exists() is False and mark_to_join is False:
                    # the user wants to remove the fanfic from this list,
                    # but it has been already deleted
                    success = True
                    message = "This fanfic has been previously removed from " \
                              "this list."

                    f = FanficList.objects.filter(list__user=act_user,
                                                  fanfic=fanfic)
                    if f.exists():
                        f = f.first()
                        list_name = f.name
                        list_id_checked = f.id
                    else:
                        list_name = None
                        list_id_checked = None
                elif fl.exists() is False and mark_to_join is True:
                    # the user wants to add the fanfic to a list, delete the
                    # old one if there is
                    FanficList.objects.filter(fanfic=fanfic,
                                              list__user=act_user).delete()
                    FanficList.objects.create(fanfic=fanfic, list=list_user)
                    success = True
                    message = "The fanfic has been added to the list."
                    list_name = list_user.name
                    list_id_checked = list_user.id

                    # send notification
                    Notification.objects.create(
                        subject=fanfic, verb="has started following",
                        target=act_user,
                        link=fanfic.get_url(),
                        in_top_bar=False, in_feed=True, reverse=True)

                success = True
        except CustomError as e:
            logger.error("Error trying to add/remove fanfic from list: {"
                         "}".format(e))
            message = e
        except Exception as e:
            message = "There was an unexpected error trying to process this " \
                      "action."
            logger.error("Error trying to add/remove fanfic from list: {"
                         "}".format(e))

        data = {
            "success": success,
            "message": message,
            "list_name": list_name,
            "list_id_checked": list_id_checked
        }
        return HttpResponse(json.dumps(data), content_type='text/plain',
                            status=200)

    def get(self, request):
        """ Manage user's lists """
        user_lists = List.objects.filter(user=request.user)
        return render(request, 'user_lists.html', {'user_lists': user_lists})

    def put(self, request):
        """ Update/create lists' names """
        new_ones = False
        try:
            with transaction.atomic():
                list_created = False
                list_changed = False
                if "new" in request.POST:
                    # new lists
                    new_lists_names = request.POST.getlist("new")
                    if len(new_lists_names) >= 1:
                        for name in new_lists_names:
                            name_clean = name.lstrip().rstrip()
                            if name_clean != "":
                                if len(name_clean) > 12:
                                    messages.error(request,
                                                   "Some of the lists "
                                                   "could not be "
                                                   "updated. The max "
                                                   "length of the name "
                                                   "is 12 characteres "
                                                   "long.")
                                else:
                                    user_list = List.objects.filter(
                                        user=request.user,
                                        name=name_clean)
                                    if user_list.exists() is True:
                                        messages.error(request,
                                                       "Some of the lists "
                                                       "could not be "
                                                       "created. There cannot"
                                                       " be two lists with "
                                                       "the "
                                                       "same name.")
                                    else:
                                        List.objects.create(user=request.user,
                                                            name=name_clean)
                                        list_created = True

                if "fieldChange" in request.POST:
                    changed_lists_ids = request.POST.get("fieldChange")
                    if len(changed_lists_ids) >= 1:
                        changed_lists_ids = changed_lists_ids.split(",")
                        for changed_list_id in changed_lists_ids:
                            id_list = int(changed_list_id)
                            list_obj = List.objects.filter(user=request.user,
                                                           id=id_list)
                            if list_obj.exists() is True:
                                list_obj = list_obj.first()
                                new_name = request.POST.get(
                                    "list" + str(id_list)).lstrip().rstrip()
                                if len(new_name) > 12 or new_name == "":
                                    messages.error(request,
                                                   "Some of the lists "
                                                   "could not be "
                                                   "updated. The max "
                                                   "length of the name "
                                                   "is 12 characteres "
                                                   "long.")
                                else:
                                    list_obj.name = new_name
                                    list_obj.save()
                                    list_changed = True

                if list_changed is True:
                    messages.success(request,
                                     "The lists have been successfully "
                                     "updated.")
                elif list_created is True:
                    messages.success(request,
                                     "The lists have been successfully "
                                     "created.")

        except CustomError as e:
            logger.error(e)
            messages.error(request, e)
        except Exception as e:
            msg = ("There was an error trying to update the user's "
                   "lists.")
            logger.error(msg + ": " + str(e))
            messages.error(request, msg)

        return redirect(reverse('lists:manage_lists'))

    def delete(self, request):
        """ Delete lists """
        try:
            with transaction.atomic():
                delete_lists_ids = request.POST.getlist("dellist")

                for delete_list_id in delete_lists_ids:
                    id_list = int(delete_list_id)
                    list_obj = List.objects.filter(user=request.user,
                                                   id=id_list)
                    if list_obj.exists() is True:
                        list_obj = list_obj.first()
                        list_obj.delete()
                messages.success(request, "The lists have been successfully "
                                          "delete.")

        except CustomError as e:
            logger.error(e)
            messages.error(request, e)
        except Exception:
            msg = ("There was an error trying to delete the user's "
                   "lists.")
            logger.error(msg)
            messages.error(request, msg)

        return redirect(reverse('lists:manage_lists'))
