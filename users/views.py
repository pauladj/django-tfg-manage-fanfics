# import the logging library
import datetime
import json
import logging
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import ListView, TemplateView

from common.decorators import anonymous_required
from common.models import Fandom, FandomFanfic, CharacterFanfic, FanficList, \
    List, Reading, Fanfic
from common.utils import CustomError, clean_integer, clean_string
from common.views import BaseView
from fandoms.forms import FilterFanficsByFandom
from notifier import models
from users.models import CustomUser, Following
from . import forms
from .forms import CustomUserCreationForm

# Get an instance of a logger
logger = logging.getLogger(__name__)


class SignUp(generic.CreateView):
    """
    View that shows sign up form
    """
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('signup_done')
    template_name = 'signup.html'


class SignUpDone(TemplateView):
    """
    View shown when sign up was successfull
    """
    template_name = 'signup_done.html'


@anonymous_required()
def check_username(request):
    """
    Checks if the username is already in use
    """
    username = request.GET.get('username')
    if not username or request.is_ajax() is False:
        return HttpResponse("Method not Allowed", status=405)
    else:
        clean_username = clean_string(username)
        if clean_username is None:
            return HttpResponse("Method not Allowed", status=405)

        if CustomUser.objects.filter(username=clean_username).exists():
            return HttpResponse(content_type='text/plain', status=404)
        else:
            return HttpResponse(content_type='text/plain', status=200)


class EditProfileUser(LoginRequiredMixin, BaseView):
    """
    Go to a user's profile edit page
    """

    def get(self, request, user_id=None):
        """ Get the modify page """
        act_user = request.user
        if int(act_user.id) != int(user_id):
            raise PermissionDenied()

        form = forms.EditUser()
        form.fields['name_surname'].initial = act_user.name_surname
        form.fields['country'].initial = act_user.country
        form.fields['date_of_birth'].initial = act_user.date_of_birth
        form.fields['gender'].initial = act_user.gender
        form.fields['website'].initial = act_user.website
        form.fields['about_me'].initial = act_user.about_me
        form.fields['email'].initial = act_user.email

        args = {'form': form, 'section': 'profile'}
        return render(request, 'edit-user.html', args)

    def put(self, request, user_id=None):
        """ Update a user profile settings """
        act_user = request.user
        if int(act_user.id) != int(user_id):
            raise PermissionDenied()
        try:
            form = forms.EditUser(request.POST)
            if form.is_valid():
                # form is ok
                act_user.name_surname = form.cleaned_data['name_surname']
                act_user.country = form.cleaned_data['country']
                act_user.date_of_birth = form.cleaned_data['date_of_birth']
                act_user.gender = form.cleaned_data['gender']
                act_user.website = form.cleaned_data['website']
                act_user.about_me = form.cleaned_data['about_me']
                email = form.cleaned_data['email']
                if email != act_user.email:
                    # email has changed
                    if CustomUser.objects.all().filter(email=email).exists():
                        raise CustomError(
                            "This email is already in the database, "
                            "choose another one.")

                password = form.cleaned_data['password']
                if password:
                    act_user.set_password(password)
            else:
                raise CustomError("Some of the fields are not valid")

            if request.FILES.get('profileImage'):
                # the user has uploaded their profile picture
                imageFile = request.FILES.get('profileImage')
                if imageFile.size > 1200000:
                    # more than 1MB
                    raise CustomError("The image size cannot" +
                                      "be more than 1MB.")

                if (imageFile.name.endswith(".jpg") or
                        imageFile.name.endswith(".png") or
                        imageFile.name.endswith(".jpeg") or
                        imageFile.name.endswith(".gif")):
                    fs = FileSystemStorage()
                    name = 'profiles/' + imageFile.name
                    filename = fs.save(name, imageFile)

                    # delete current avatar image
                    old_image = act_user.avatar.name
                    if old_image != "profiles/default.png":
                        fs.delete(old_image)

                    act_user.avatar = filename
                else:
                    raise CustomError(
                        "Only .jpg, .jpeg, .png and .gif are " +
                        "accepted for the profile image.")
            act_user.save()

            messages.success(
                request, "The profile was successfully updated.")
            return redirect("edit_profile_user", user_id=user_id)
        except CustomError as e:
            logger.error("Error updating a profile. {}".format(e))
            messages.error(request, e)
            args = {'form': form, 'section': 'profile'}
            return render(request, 'edit-user.html', args)
        except Exception as e:
            logger.error("Error updating a profile. {}".format(e))
            messages.error(request, "There was an error updating the profile.")
            args = {'form': form, 'section': 'profile'}
            return render(request, 'edit-user.html', args)


class EditGeneralSettingsUser(LoginRequiredMixin, BaseView):
    """
    Go to a user's general settings edit page
    """

    def get(self, request, user_id=None):
        """ Get the modify page """
        act_user = request.user
        if int(act_user.id) != int(user_id):
            raise PermissionDenied()

        args = {'section': 'general'}
        return render(request, 'edit-user.html', args)

    def put(self, request, user_id=None):
        """ Update a user general settings """
        act_user = request.user
        if int(act_user.id) != int(user_id):
            raise PermissionDenied()
        try:
            privacy_value = clean_integer(request.POST.get("rsvp"))
            if privacy_value is None or privacy_value not in [1, 2, 3]:
                # error
                raise CustomError(
                    "There was an error trying to save the new settings.")

            act_user.privacy = privacy_value
            act_user.save()

            messages.success(
                request, "The profile was successfully updated.")
            return redirect("edit_general_user", user_id=user_id)
        except CustomError as e:
            logger.error("Error updating a profile. {}".format(e))
            messages.error(request, e)
            args = {'section': 'general'}
            return render(request, 'edit-user.html', args)
        except Exception as e:
            logger.error("Error updating a profile. {}".format(e))
            messages.error(request, "There was an error updating the profile.")
            args = {'section': 'profile'}
            return render(request, 'edit-user.html', args)


class GetBackupUserData(LoginRequiredMixin, BaseView):
    """
    Get a user's data backup
    """

    def get(self, request, user_id=None):
        """ Get the user file """
        act_user = request.user
        if int(act_user.id) != int(user_id):
            raise PermissionDenied()

        app_list = {}

        app_list['chapters_readings'] = list(Reading.objects.filter(
            user=act_user).values('chapter__fanfic__name', 'private_notes',
                                  'read', 'chapter__num_chapter',
                                  'chapter__url_chapter'))
        added_fanfics = FanficList.objects.filter(
            list__user=act_user).values_list('fanfic__id', flat=True)
        app_list['fanfics_in_lists'] = list(FanficList.objects.filter(
            list__user=act_user).values('list__name', 'fanfic__name'))
        app_list['fanfics'] = list(Fanfic.objects.filter(
            id__in=added_fanfics).values(
            'name', 'web'))

        response = HttpResponse(json.dumps(
            app_list), content_type='application/json')
        response['Content-Disposition'] = 'attachment; ' \
                                          'filename="fickeeper_backup{' \
                                          '}.json"'.format(
            str(datetime.datetime.now().strftime(
                '%Y%m%d%H%M%S%f'))
        )

        return response


class Profile(LoginRequiredMixin, ListView):
    """
    A user's profile
    """
    template_name = 'profile.html'
    context_object_name = "user_notifications"
    paginate_by = 10

    def get_queryset(self):
        u = CustomUser.objects.get(id=self.kwargs['user_id'])
        a = models.Notification.objects.filter(in_feed=True).filter(
            Q(subject_user=u) | Q(target=u)).order_by('-when')
        return a

    def get_context_data(self, **kwargs):
        context = super(Profile, self).get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        context['user_profile'] = CustomUser.objects.get(
            id=user_id)
        see = True
        user = get_object_or_404(CustomUser, id=user_id)
        if user.id != self.request.user.id:
            if user.privacy == 3:
                # nobody can see this user's fanfics
                see = False
            elif user.privacy == 1:
                # if the propietary of the library follows the request user
                if user.follows(self.request.user) is False:
                    see = False
        context['see'] = see
        return context


@login_required(redirect_field_name=None, login_url='login')
def follow_user(request):
    """
    Follow a user
    """
    target_id = request.POST.get('targetId')
    act_user = request.user

    if not target_id or not act_user or request.is_ajax() is False:
        return HttpResponse("Method not Allowed", status=405)
    else:
        target_id = clean_integer(target_id)
        if target_id is None:
            return HttpResponse("Method not Allowed", status=405)

        target_user = CustomUser.objects.get(id=target_id)
        if act_user == target_user:
            return HttpResponse("Method not Allowed", status=405)

        already_following = Following.objects.filter(
            user_one=act_user, user_two=target_user).exists()

        if already_following is True:
            action = 'deleted'
            Following.objects.filter(
                user_one=act_user, user_two=target_user).delete()
        else:
            action = 'created'
            Following.objects.create(
                user_one=act_user, user_two=target_user)

            # send notification
            source = act_user
            target = target_user
            models.Notification.objects.create(
                subject=source, verb="has followed", target=target,
                subject_user=source,
                link=source.get_link(),
                in_top_bar=True, in_feed=True)

        return HttpResponse(content=action, content_type='text/plain',
                            status=200)


class FanficsOfUser(LoginRequiredMixin, ListView):
    """ Show fanfics of user """
    template_name = 'fanfics_of_user.html'
    context_object_name = "fanfics"
    paginate_by = 15

    def get_queryset(self):

        user_id = int(self.kwargs['user_id'])

        self.user = get_object_or_404(CustomUser, id=user_id)
        if self.user.id != self.request.user.id:
            if self.user.privacy == 3:
                # nobody can see this user's fanfics
                raise PermissionDenied()
            elif self.user.privacy == 1:
                # if the propietary of the library follows the request user
                if self.user.follows(self.request.user) is False:
                    raise PermissionDenied()

        try:
            # get the queryset filtered
            self.fandom = None
            self.list_chose = None

            if "fandom_id" in self.request.GET:

                self.fandom = Fandom.objects.filter(id=self.request.GET.get(
                    'fandom_id'))
                if self.fandom.exists() is False:
                    raise Exception("There was an unexpected error.")

                self.fandom = self.fandom.first()

                fanfics_ids = list(FandomFanfic.objects.filter(
                    fandom=self.fandom).values_list('fanfic__id', flat=True))

                if "list" in self.request.GET:
                    # FILTER BY LIST
                    list_id = int(self.request.GET.get('list'))
                    if list_id == 0 or list_id == "0":
                        # all the fanfics, doesn't matter the list
                        fanfics = FanficList.objects.filter(
                            list__user=self.user, fanfic__id__in=fanfics_ids)
                    else:
                        list_obj = List.objects.filter(id=list_id,
                                                       user=self.user)
                        if list_obj.exists() is False:
                            # this list does not exist, or the user is not the
                            # propietary
                            raise PermissionDenied()

                        list_obj = list_obj.first()
                        self.list_chose = list_obj.id
                        fanfics = FanficList.objects.filter(
                            list=list_obj, fanfic__id__in=fanfics_ids)
                else:
                    fanfics = FanficList.objects.filter(
                        list__user=self.user, fanfic__id__in=fanfics_ids)

                if 'sort_by' in self.request.GET:
                    form = FilterFanficsByFandom(self.request.GET)
                    if form.is_valid():
                        sort_by = form.cleaned_data.get('sort_by', 0)
                        language = form.cleaned_data.get('language', 0)
                        genre = form.cleaned_data.get('genre', 0)
                        length = form.cleaned_data.get('length', 0)
                        status = form.cleaned_data.get('status', 0)
                        rating = form.cleaned_data.get('rating', 0)
                        character_a = form.cleaned_data.get('character_a', 0)
                        character_b = form.cleaned_data.get('character_b', 0)

                        # LANGUAGE
                        if language != 0 and language != "0":
                            fanfics = fanfics.filter(
                                fanfic__language__iexact=language)

                        # GENRE
                        if genre != 0 and genre != "0":
                            fanfics = fanfics.filter(Q(
                                fanfic__genre1__iexact=genre) | Q(
                                fanfic__genre2__iexact=genre) | Q(
                                fanfic__genre3__iexact=genre) | Q(
                                fanfic__genre4__iexact=genre))

                        # LENGTH
                        words = 1000
                        if length == "0" or length == 0:
                            pass
                        elif length == "1" or length == 1:
                            # < 1K words
                            words = 1000
                            fanfics = fanfics.filter(
                                fanfic__num_words__lt=words)
                        else:
                            if length == "2" or length == 2:
                                # > 10K words
                                words = 10000
                            elif length == "3" or length == 3:
                                # > 40K words
                                words = 40000
                            elif length == "4" or length == 4:
                                # > 60K words
                                words = 60000
                            elif length == "5" or length == 5:
                                # > 100K words
                                words = 100000
                            fanfics = fanfics.filter(
                                fanfic__num_words__gte=words)

                        # STATUS
                        if status == 1 or status == "1":
                            # complete
                            fanfics = fanfics.filter(fanfic__complete=True)
                        elif status == 2 or status == "2":
                            # in progress
                            fanfics = fanfics.exclude(fanfic__complete=True)

                        # RATING
                        if rating == 1 or rating == '1':
                            # K
                            fanfics = fanfics.filter(fanfic__rating='K')
                        elif rating == 2 or rating == '2':
                            # K+
                            fanfics = fanfics.filter(fanfic__rating='K+')
                        elif rating == 3 or rating == '3':
                            # T
                            fanfics = fanfics.filter(fanfic__rating='T')
                        elif rating == 4 or rating == '4':
                            # M
                            fanfics = fanfics.filter(fanfic__rating='M')

                        # CHARACTER A & B
                        fanfics_ids = None
                        if character_a != 0 and character_a != "0" \
                                and character_b != "0" and character_b != 0:
                            fanfics_ids = CharacterFanfic.objects.filter(Q(
                                character__id=character_a) | Q(
                                character__id=character_b)).values_list(
                                'fanfic__id', flat=True)
                        elif character_a != 0:
                            fanfics_ids = CharacterFanfic.objects.filter(
                                character__id=character_a).values_list(
                                'fanfic__id', flat=True)
                        elif character_b != 0:
                            fanfics_ids = CharacterFanfic.objects.filter(
                                character__id=character_b).values_list(
                                'fanfic__id', flat=True)
                        if fanfics_ids is not None:
                            fanfics = fanfics.filter(
                                fanfic__id__in=fanfics_ids)

                        # SORT BY
                        if sort_by == '1' or sort_by == 1:
                            # sort by last updated
                            fanfics = fanfics.order_by(
                                '-fanfic__last_time_updated')
                        elif sort_by == 2 or sort_by == '2':
                            # sort by number of reviews
                            fanfics = sorted(fanfics,
                                             key=lambda t:
                                             t.fanfic.get_num_reviews(),
                                             reverse=True)
                        elif sort_by == 3 or sort_by == '3':
                            # sort by number of followers
                            fanfics = sorted(fanfics,
                                             key=lambda t:
                                             t.fanfic.get_num_of_users(),
                                             reverse=True)
                        else:
                            fanfics = fanfics.order_by('id')

                        return fanfics
                    else:
                        raise Exception("There was an unexpected error.")

                fanfics = fanfics.order_by('id')
                return fanfics

            else:
                return []

        except Exception:
            messages.error(self.request, "There was an unexpected error "
                                         "trying to filter the fanfics.")

        return []

    def get_context_data(self, **kwargs):
        context = super(FanficsOfUser, self).get_context_data(**kwargs)
        context['fanfics_user'] = self.user
        context['fandom'] = self.fandom
        context['form_filter'] = FilterFanficsByFandom(data=self.request.GET)
        context['list_chose'] = self.list_chose
        context['menu'] = "my_fics"

        query_string_params = self.request.META['QUERY_STRING']
        if "page" in query_string_params:
            query_string_params_two = re.compile("^page=\d+&?").split(
                query_string_params)
            if len(query_string_params_two) == 2:
                query_string_params_two = query_string_params_two[1]
            else:
                query_string_params_two = ''
        else:
            query_string_params_two = query_string_params
        context['pagination_append'] = "&" + query_string_params_two

        return context
