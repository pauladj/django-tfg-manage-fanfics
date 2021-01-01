import json
from unittest import mock

from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from common.models import Fanfic, FandomFanfic, Fandom, Type, Character, \
    SubmittedReport
from users.models import CustomUser


class AddExternalFanficTests(TestCase):

    def setUp(self):
        self.normal_user = CustomUser.objects.create(
            name_surname="name",
            country="AM",
            date_of_birth="2000-07-02",
            email="em@gm.com",
            username='testuser',
            password="12345")

        Fanfic.objects.create(name="Testek fanfic", author="michaelRuiz",
                              web="http://web-fanfic.com", genre1="adv",
                              complete=True)

        self.client = Client()
        self.client.force_login(user=self.normal_user)

    def test_external_add_status_code(self):
        response = self.client.get(reverse('fanfics:external_add'))
        self.assertEqual(response.status_code, 200)

    @mock.patch('fanfics.custom_models.FanficWeb.url_without_errors')
    def test_post_external_add_bad_url(self, mock_url_without_errors):
        ''' Try to add fanfic with bad url '''
        mock_url_without_errors.return_value = "Error: bad url"

        post_data = {'url_fanfic': 'bad-url'}

        response = self.client.post(reverse('fanfics:external_add'),
                                    data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_external_fanfic.html')

    @mock.patch('fanfics.custom_models.FanficWeb.get_cleaned_url')
    @mock.patch('fanfics.custom_models.FanficWeb.url_without_errors')
    def test_post_external_add_already_added(self,
                                             mock_url_without_errors,
                                             mock_cleaned_url):
        """ Try to add fanfic that has similar ones """
        mock_url_without_errors.return_value = "http://web-fanfic.com"
        mock_cleaned_url.return_value = "http://web-fanfic.com"

        post_data = {'url_fanfic': 'http://web-fanfic.com'}

        response = self.client.post(reverse('fanfics:external_add'),
                                    data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_external_fanfic.html')

    @mock.patch('fanfics.custom_models.FanficWeb.get_cleaned_url')
    @mock.patch('common.tasks.scrape_and_add_fanfic.delay')
    @mock.patch('fanfics.custom_models.FanficWeb.check_if_online')
    @mock.patch('fanfics.custom_models.FanficWeb.url_without_errors')
    def test_post_external_add_good_url(self, mock_url_without_errors,
                                        mock_check_if_online, mock_scrape,
                                        mock_cleaned_url):
        """ Try to add fanfic """
        mock_url_without_errors.return_value = "http://web-ok.com"
        mock_check_if_online.return_value = True
        mock_scrape.return_value = ""
        mock_cleaned_url.return_value = "http://web-ok.com"

        post_data = {'url_fanfic': 'http://web-ok.com'}

        response = self.client.post(reverse('fanfics:external_add'),
                                    data=post_data)
        self.assertRedirects(response, reverse('fanfics:external_done'))


class AddExternalFanficDoneTests(TestCase):

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

    def test_external_add_done_status_code(self):
        """ Check if the success page after adding a fanfic is showing up """
        response = self.client.get(reverse('fanfics:external_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_external_fanfic_done.html')


class FanficViewTest(TestCase):

    def setUp(self):
        self.normal_user = CustomUser.objects.create(
            name_surname="name",
            country="AM",
            date_of_birth="2000-07-02",
            email="em@gm.com",
            username='testuser',
            password="12345")

        self.fanfic = Fanfic.objects.create(name="Testek fanfic",
                                            author="michaelRuiz",
                                            web="http://web-fanfic.com",
                                            genre1="adv",
                                            complete=True)
        self.type = Type.objects.create(name="test_type")
        self.fandom = Fandom.objects.create(name="Test fandom",
                                            type=self.type)

        self.fandom_fanfic = FandomFanfic.objects.create(fandom=self.fandom,
                                                         fanfic=self.fanfic,
                                                         is_primary=True)

        self.client = Client()
        self.client.force_login(user=self.normal_user)

    def test_fanfic_page_status_code(self):
        ''' Test show a fanfic '''
        response = self.client.get(reverse(
            'fanfics:fanfic', kwargs={'fanfic_id': self.fanfic.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fanfic.html')

    def test_submit_error(self):
        """ Test submit error of a fanfic """
        data = {
            "issue": "m",
            "comment": "Just a comment"
        }
        response = self.client.post(reverse('fanfics:fanfic_errors',
                                            kwargs={
                                                'fanfic_id': self.fanfic.id}),
                                    data=data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fanfic.html')
        submitted_report = SubmittedReport.objects.all().first()
        self.assertEqual(submitted_report.issue, "m")
        self.assertEqual(submitted_report.comment, "Just a comment")


class FanficCharactersViewTest(TestCase):

    def setUp(self):
        self.normal_user = CustomUser.objects.create(
            name_surname="name",
            country="AM",
            date_of_birth="2000-07-02",
            email="em@gm.com",
            username='testuser',
            password="12345")

        self.fanfic = Fanfic.objects.create(name="Testek fanfic",
                                            author="michaelRuiz",
                                            web="http://web-fanfic.com",
                                            genre1="adv",
                                            complete=True)
        self.type = Type.objects.create(name="test_type")
        self.fandom = Fandom.objects.create(name="Test fandom",
                                            type=self.type)

        self.fandom_fanfic = FandomFanfic.objects.create(fandom=self.fandom,
                                                         fanfic=self.fanfic,
                                                         is_primary=True)

        Character.objects.create(name_surname="testcharacter",
                                 fandom=self.fandom)

        self.client = Client()
        self.client.force_login(user=self.normal_user)

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_get_possible_characters_for_a_fanfic(self, mock_ajax):
        """ Test get possible characters for a fanfic """
        mock_ajax.return_value = True

        response = self.client.get(reverse(
            'fanfics:fanfic_characters', kwargs={'fanfic_id': self.fanfic.id}))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response['values']), 1)
