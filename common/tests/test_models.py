from django.test import TestCase
from users.models import CustomUser
from common.models import Fanfic
from django.test.client import Client


class FanficTests(TestCase):

    def setUp(self):
        self.normal_user = CustomUser.objects.create(
            name_surname="name",
            country="AM",
            date_of_birth="2000-07-02",
            email="em@gm.com",
            username='testuser',
            password="12345")

        self.one_fanfic = Fanfic.objects.create(
                                name="Testek1 fanfic",
                                author="michaelRuiz",
                                web="http://webfanfic.com/jkas",
                                genre1="adv",
                                complete=True)

        self.two_fanfic = Fanfic.objects.create(
                                name="Testek2 fanfic",
                                author="michaelRuiz",
                                web="www.web2fanfic.org/sldkf",
                                genre1="adv",
                                complete=True)

        self.three_fanfic = Fanfic.objects.create(
                                name="Testek3 fanfic",
                                author="michaelRuiz",
                                web="https://www.web3fanfic.com/slkdf",
                                genre1="adv",
                                complete=True)

        self.client = Client()
        self.client.force_login(user=self.normal_user)

    def test_str(self):
        ''' Test if name is well set '''
        self.assertEqual(self.one_fanfic.name, "Testek1 fanfic")

    def test_get_domain(self):
        ''' Test if the domain is well obtained '''
        self.assertEqual(self.one_fanfic.get_domain(), "webfanfic")
        self.assertEqual(self.two_fanfic.get_domain(), "web2fanfic")
        self.assertEqual(self.three_fanfic.get_domain(), "web3fanfic")

    def test_is_genre_option(self):
        """ Check if the parameter it's a genre """
        is_genre = Fanfic.is_genre_option("drama")
        self.assertTrue(is_genre)

    def test_is_not_genre_option(self):
        """ Check if the parameter it's not a genre """
        is_genre = Fanfic.is_genre_option("nogenre")
        self.assertFalse(is_genre)

    def test_get_abbreviation_from_genre_name(self):
        """ Test if the abbreviation of genre is well obtained """
        abbreviation = Fanfic.get_abbreviation_from_genre_name("drama")
        self.assertEqual(abbreviation, "dra")
