from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from common.models import Fanfic, Type, Fandom, Character, FandomFanfic, \
    CharacterFanfic
from users.models import CustomUser


class FanficsOfFandomViewTests(TestCase):

    def setUp(self):
        self.normal_user = CustomUser.objects.create(
            name_surname="name",
            country="AM",
            date_of_birth="2000-07-02",
            email="em@gm.com",
            username='testuser',
            password="12345")

        self.client = Client()
        self.client.force_login(user=self.normal_user)

        self.type = Type.objects.create(name="testType")
        self.fandom = Fandom.objects.create(name="test_fandom",
                                            type=self.type)
        self.fanfic = Fanfic.objects.create(name="Testek fanfic",
                                            author="michaelRuiz",
                                            web="http://web-fanfic.com",
                                            genre1="adv",
                                            complete=True)
        self.character = Character.objects.create(name_surname="test "
                                                               "character",
                                                  fandom=self.fandom)
        FandomFanfic.objects.create(fandom=self.fandom, fanfic=self.fanfic,
                                    is_primary=True)
        CharacterFanfic.objects.create(character=self.character,
                                       fanfic=self.fanfic)

    def test_fanfics_of_fandom_view_status_code(self):
        """ Test show fanfics of fandom """
        response = self.client.get(reverse('fandoms:fanfics', kwargs={
            'fandom_id': self.fandom.id}))
        self.assertEqual(response.status_code, 200)

    def test_fanfics_of_fandom_filter(self):
        """ Test show fanfics of fandom """
        data = {
            'sort_by': 0,
            'genre': 'adv',
            'status': 1
        }
        response = self.client.get(reverse('fandoms:fanfics', kwargs={
            'fandom_id': self.fandom.id}), data=data)
        self.assertEqual(response.status_code, 200)
