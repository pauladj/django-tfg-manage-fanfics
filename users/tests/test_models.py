from django.test import TestCase
from ..models import CustomUser


class CustomUserTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(
            name_surname="Testing user",
            username="testuser", email="test@test",
            country="US", date_of_birth="1997-12-08",
            password="A1.aaaaa")

        self.user2 = CustomUser.objects.create(
            name_surname="Testing user2",
            username="testuser2", email="test2@test",
            country="US", date_of_birth="1997-12-08",
            password="A1.aaaaa")

    def test_retrieve_username(self):
        """The username is retrieved correctly"""
        self.assertEqual(self.user.username, "testuser")

    def test_get_num_fanfics_added(self):
        """The num of fanfics added """
        self.assertEqual(self.user.get_num_fanfics_added(), 0)

    def test_get_num_reviews_written(self):
        """The num of written reviews """
        self.assertEqual(self.user.get_num_reviews_written(), 0)

    def test_get_num_follows(self):
        """The num of follows """
        self.assertEqual(self.user.get_num_of_follows(), 0)

    def test_get_num_of_followers(self):
        """The num of followers """
        self.assertEqual(self.user.get_num_of_followers(), 0)

    def test_get_follows(self):
        """The num of fanfics added """
        self.assertEqual(self.user.follows(self.user2), 0)
