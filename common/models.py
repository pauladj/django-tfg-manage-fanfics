import datetime
import re

from django.db import models
from django.shortcuts import reverse

from common.choices import GENRE, RATING, ISSUES
from users.models import CustomUser


class Type(models.Model):
    name = models.CharField(max_length=10, primary_key=True)

    class Meta:
        verbose_name = "Media types"
        verbose_name_plural = "Media types"

    def __str__(self):
        return self.name

    def get_url(self):
        """ Get link of the type """
        return reverse('media_type:fandoms', kwargs={'media_type':
                                                         self.name})


class Fandom(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)

    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='fanfics', default='profiles/default.png')

    class Meta:
        unique_together = [['name', 'type']]

    def __str__(self):
        return self.name

    def get_url(self):
        """ Get the link of the fandom """
        return reverse('fandoms:fanfics', kwargs={'fandom_id':
                                                      self.id})

    def get_image(self):
        """ Get the representative image """
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url


class Character(models.Model):
    id = models.AutoField(primary_key=True)
    name_surname = models.CharField(max_length=255, blank=False,
                                    null=False)
    fandom = models.ForeignKey(Fandom, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_surname

    class Meta:
        unique_together = [['name_surname', 'fandom']]


class Fanfic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    author = models.CharField(max_length=255, blank=False, null=False)
    web = models.CharField(max_length=255, blank=False, null=False,
                           unique=True)
    language = models.CharField(max_length=255, blank=True, null=True)

    complete = models.BooleanField(default=False)

    genre1 = models.CharField(
        choices=GENRE, max_length=3, blank=True, null=True)
    genre2 = models.CharField(
        choices=GENRE, max_length=3, blank=True, null=True)
    genre3 = models.CharField(
        choices=GENRE, max_length=3, blank=True, null=True)
    genre4 = models.CharField(
        choices=GENRE, max_length=3, blank=True, null=True)

    last_time_checked = models.DateTimeField(blank=False, null=False,
                                             default=datetime.datetime.now)

    last_time_updated = models.DateTimeField(blank=True, null=True)
    num_words = models.IntegerField(blank=True, null=True)

    rating = models.CharField(max_length=2, choices=RATING, blank=True,
                              null=True)
    average_score = models.FloatField(blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        primary_fandom = self.get_primary_fandom()
        if primary_fandom is None:
            return self.name
        primary_fandom = str(primary_fandom)
        secondary_fandom = self.get_secondary_fandom()
        secondary_fandom = "" if secondary_fandom is None else (
                ", " + str(secondary_fandom))

        return (self.name + " (" + primary_fandom +
                secondary_fandom + ")")

    def num_chapters(self):
        """ Get number of chapter of this fanfic """
        return Chapter.objects.filter(fanfic=self).count()

    def get_domain(self):
        ''' Returns the domain of where it's hosted '''
        regex = "(http[s]?|www\.)"
        split_url = re.compile(regex).split(self.web)
        split_url = split_url[len(split_url) - 1]

        regex = "(:?[\/]{2})"
        split_url = re.compile(regex).split(split_url)
        split_url = split_url[len(split_url) - 1]

        regex = "\.[\D]{3}\/"
        split_url = re.compile(regex).split(split_url)
        domain_name = split_url[0]

        return domain_name

    def add_genre(self, genre):
        ''' Add one genre to the fanfic '''
        abbr = Fanfic.get_abbreviation_from_genre_name(genre)
        if abbr is not None:
            if self.genre1 is None:
                self.genre1 = abbr
            elif self.genre2 is None:
                self.genre2 = abbr
            elif self.genre3 is None:
                self.genre3 = abbr
            elif self.genre4 is None:
                self.genre4 = abbr

    @staticmethod
    def is_genre_option(genre):
        ''' Check if the parameter it's a genre '''
        choices = list(Fanfic._meta.get_field('genre1').choices)
        choices = [x[1] for x in choices]
        return genre in choices

    @staticmethod
    def get_abbreviation_from_genre_name(genre):
        ''' Get the abbreviation to save knowing the name '''
        choices = list(Fanfic._meta.get_field('genre1').choices)
        abbreviation = [x[0] for x in choices if x[1] == genre]
        if abbreviation:
            abbreviation = abbreviation[0]
        else:
            abbreviation = None
        return abbreviation

    def get_image(self):
        """ Get the representative image """
        return self.get_primary_fandom().get_image()

    def get_url(self):
        """ Get the link of the fanfic """
        return reverse('fanfics:fanfic', kwargs={'fanfic_id': self.id})

    def get_primary_fandom(self):
        """ Get the primary fandom of the fanfic """
        f = FandomFanfic.objects.filter(fanfic=self,
                                        is_primary=True)
        if f.exists():
            return f.first().fandom

    def get_secondary_fandom(self):
        """ Get the secondary fandom of the fanfic """
        fandom_fanfic = FandomFanfic.objects.filter(fanfic=self,
                                                    is_primary=False)
        if fandom_fanfic.exists():
            return fandom_fanfic.first().fandom
        else:
            return

    def get_num_reviews(self):
        """ Get the number of reviews """
        return Review.objects.filter(fanfic=self).count()

    def get_num_of_users(self):
        """ Get the number of users who added this """
        return FanficList.objects.filter(fanfic=self).count()

    def get_num_of_chapters(self):
        """ Get the number of chapters """
        return Chapter.objects.filter(fanfic=self).count()

    def get_characters(self):
        """ Get the characters of the fanfic """
        return CharacterFanfic.objects.filter(fanfic=self)

    def get_pairings(self):
        """ Get the pairings """
        return Pairing.objects.filter(fanfic=self)


class Pairing(models.Model):
    fanfic = models.ForeignKey(Fanfic, on_delete=models.CASCADE)
    character_one = models.ForeignKey(
        Character, on_delete=models.CASCADE,
        related_name="character_pairing_one")
    character_two = models.ForeignKey(
        Character, on_delete=models.CASCADE,
        related_name="character_pairing_two")

    def __str__(self):
        return "(" + self.character_one.name_surname + ", " + \
               self.character_two.name_surname + ")"

    class Meta:
        unique_together = [['fanfic', 'character_one', 'character_two']]


class CharacterFanfic(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    fanfic = models.ForeignKey(Fanfic, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Characters in Fanfics'
        verbose_name_plural = 'Characters in Fanfics'
        unique_together = [['character', 'fanfic']]

    def __str__(self):
        return self.character.name_surname + " (" + self.fanfic.name + ")"


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(blank=True, null=True)
    score = models.FloatField(default=0)
    date = models.DateField(auto_now=True)
    fanfic = models.ForeignKey(Fanfic, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['user', 'fanfic']]

    def __str__(self):
        return "{}'s review".format(self.user)

    def get_url(self):
        return reverse('reviews:reviews', kwargs={'review_id': self.id})


class FandomFanfic(models.Model):
    fandom = models.ForeignKey(Fandom, on_delete=models.CASCADE)
    fanfic = models.ForeignKey(Fanfic, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=True)

    class Meta:
        unique_together = [['fandom', 'fanfic']]

    def __str__(self):
        return "{} ({})".format(self.fanfic.name, self.fandom.name)


class Related(models.Model):
    fanfic_one = models.ForeignKey(Fanfic, on_delete=models.CASCADE,
                                   related_name="fanfic_one")
    fanfic_two = models.ForeignKey(Fanfic, on_delete=models.CASCADE,
                                   related_name="fanfic_two")


class Chapter(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    num_chapter = models.IntegerField(blank=False, null=False)
    url_chapter = models.CharField(max_length=255, blank=True, null=True)
    fanfic = models.ForeignKey(Fanfic, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)

    class Meta:
        unique_together = [['num_chapter', 'fanfic']]

    def __str__(self):
        if self.title is None:
            return ""
        else:
            return self.title

    def get_reading_of_user(self, user):
        """ Get the reading relation from one user for this chapter"""
        try:
            reading = Reading.objects.get(chapter=self, user=user)
        except Reading.DoesNotExist:
            reading = None
        return reading


class Reading(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    private_notes = models.TextField(blank=True, null=True)
    read = models.BooleanField(default=False)

    class Meta:
        unique_together = [['chapter', 'user']]


class List(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = [['name', 'user']]


class FanficList(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    fanfic = models.ForeignKey(Fanfic, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)


class SubmittedReport(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fanfic = models.ForeignKey(Fanfic, on_delete=models.CASCADE)
    issue = models.CharField(
        choices=ISSUES, max_length=2)
    comment = models.TextField()
    date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Submitted reports"
        verbose_name_plural = "Submitted reports"
