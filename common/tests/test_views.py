from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from users.models import CustomUser


class DashboardTests(TestCase):

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

    def test_home_status_code(self):
        response = self.client.get(reverse('common:home'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_status_code(self):
        response = self.client.get(reverse('common:dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)


class SearchTests(TestCase):

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

    def test_search_status_code(self):
        response = self.client.get(reverse('common:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_user(self):
        """ Test search user """
        data = {
            "where": "user",
            "text": "test"
        }
        response = self.client.get(reverse('common:search'), data)
        self.assertEqual(response.status_code, 200)

    def test_search_fanfic(self):
        """ Test search fanfic"""
        data = {
            "where": "fanfic",
            "text": "test"
        }
        response = self.client.get(reverse('common:search'), data)
        self.assertEqual(response.status_code, 200)

    def test_search_empty(self):
        """ Test search empty"""
        data = {
            "text": ""
        }
        response = self.client.get(reverse('common:search'), data)
        self.assertEqual(response.status_code, 200)

    def test_search_with_error(self):
        """ Test search with error """
        response = self.client.get(reverse('common:search'))
        self.assertEqual(response.status_code, 200)
