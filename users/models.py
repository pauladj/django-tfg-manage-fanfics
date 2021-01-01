from datetime import date

from django.apps import apps
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from .validators import date_of_birth_validator


class CustomUserManager(UserManager):
    pass


class CustomUser(AbstractUser):
    name_surname = models.CharField(_('full name'), max_length=180,
                                    blank=False)
    country = CountryField(blank=False, blank_label='Select country')
    date_of_birth = models.DateField(blank=False,
                                     validators=[date_of_birth_validator])
    email = models.EmailField(_('email address'), blank=False, unique=True)
    website = models.CharField(
        _('my website'), max_length=255, blank=True, null=True)
    GENDER_OPTIONS = (
        ('m', 'Male'),
        ('f', 'Female')
    )
    gender = models.CharField(
        choices=GENDER_OPTIONS, max_length=1, blank=True, null=True)
    about_me = models.TextField(_('about me'), blank=True, null=True)
    avatar = models.ImageField(
        upload_to='profiles', default='profiles/default.png')

    PRIVACY_OPTIONS = (
        (1, 'following'),
        (2, 'all'),
        (3, 'nobody')
    )
    privacy = models.IntegerField(
        choices=PRIVACY_OPTIONS, default=2)

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def get_image(self):
        """ Get the representative image """
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url

    def get_num_fanfics_added(self):
        """ Get the number of fanfics added """
        FanficList = apps.get_model('common.FanficList')
        user_num_fanfics = FanficList.objects.filter(
            list__user=self).count()
        return user_num_fanfics

    def get_num_reviews_written(self):
        """ Get the number of reviews written """
        Review = apps.get_model('common.Review')
        user_num_reviews = Review.objects.filter(user=self).count()
        return user_num_reviews

    def get_num_of_follows(self):
        """ Get the number of the people they follow """
        user_num_follows = Following.objects.filter(user_one=self).count()
        return user_num_follows

    def get_follows(self):
        """ Get the people they follow """
        return Following.objects.filter(user_one=self).order_by(
            'user_two__username')

    def get_num_of_followers(self):
        """ Get the number of followers """
        user_num_followers = Following.objects.filter(user_two=self).count()
        return user_num_followers

    def get_followers(self):
        """ Get the followers """
        return Following.objects.filter(user_two=self).order_by(
            'user_one__username')

    def get_how_old(self):
        """ Get how old they are """
        today = date.today()
        born = self.date_of_birth
        years_now = today.year - born.year - \
                    ((today.month, today.day) < (born.month, born.day))
        return years_now

    def get_three_favorites_fanfics(self):
        """ Get three favorites fanfics """
        Review = apps.get_model('common.Review')
        three_fanfics = Review.objects.filter(
            user=self, score__isnull=False).exclude(score__lt=3).order_by(
            '-score')[:3]
        return three_fanfics

    def get_three_favorites_fandoms(self):
        """ Get three favorites fandoms """
        reviews = self.get_three_favorites_fanfics()

        fandoms = [x.fanfic.get_primary_fandom() for x in reviews if
                   x.fanfic.get_primary_fandom() is not None]
        return list(set(fandoms))

    def follows(self, two):
        """ True if the user follows two """
        return Following.objects.filter(user_one=self,
                                        user_two=two).exists()

    def get_link(self):
        """ Get the profile link """
        return reverse('profile', kwargs={'user_id': self.id})


class Following(models.Model):
    user_one = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                 null=True,
                                 related_name="user_one_following")
    user_two = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                 null=True,
                                 related_name="user_two_following")
    date = models.DateField(auto_now=True)
