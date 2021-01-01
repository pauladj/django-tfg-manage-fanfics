import json
from unittest import mock

from django.test import Client, TestCase
from django.urls import reverse

from common.models import Fanfic, Type, Fandom, FandomFanfic, List, FanficList
from users.models import CustomUser


class ListsViewTest(TestCase):

    def setUp(self):
        self.normal_user = CustomUser.objects.create(
            name_surname="name2",
            country="AM",
            date_of_birth="2000-07-02",
            email="em2@gm.com",
            username='testuser3',
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

        self.list = List.objects.create(name='Test list',
                                        user=self.normal_user)

        self.client = Client()
        self.client.force_login(user=self.normal_user)

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_add_fanfic_to_a_list(self, mock_ajax):
        """ Test add fanfic to a list """
        mock_ajax.return_value = True

        data = {
            'fanficId': self.fanfic.id,
            'join': 'true'
        }

        response = self.client.post(reverse(
            'lists:lists', kwargs={'list_id': self.list.id}), data=data)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertTrue(json_response['success'])
        self.assertTrue(FanficList.objects.filter(fanfic=self.fanfic,
                                                  list=self.list).exists())

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_remove_from_list_but_already_done(self, mock_ajax):
        """ Test remove from list even if already done """
        mock_ajax.return_value = True

        data = {
            'fanficId': self.fanfic.id,
            'join': 'false'
        }

        response = self.client.post(reverse(
            'lists:lists', kwargs={'list_id': self.list.id}), data=data)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertTrue(json_response['success'])
        self.assertFalse(FanficList.objects.filter(fanfic=self.fanfic,
                                                   list=self.list).exists())

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_remove_from_list(self, mock_ajax):
        """ Test remove from list """
        mock_ajax.return_value = True

        FanficList.objects.create(fanfic=self.fanfic, list=self.list)

        data = {
            'fanficId': self.fanfic.id,
            'join': 'false'
        }

        response = self.client.post(reverse(
            'lists:lists', kwargs={'list_id': self.list.id}), data=data)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertTrue(json_response['success'])
        self.assertFalse(FanficList.objects.filter(fanfic=self.fanfic,
                                                   list=self.list).exists())

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_add_even_already_added(self, mock_ajax):
        """ Test add to list even if already added """
        mock_ajax.return_value = True

        FanficList.objects.create(fanfic=self.fanfic, list=self.list)

        data = {
            'fanficId': self.fanfic.id,
            'join': 'true'
        }

        response = self.client.post(reverse(
            'lists:lists', kwargs={'list_id': self.list.id}), data=data)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertTrue(json_response['success'])
        self.assertTrue(FanficList.objects.filter(fanfic=self.fanfic,
                                                  list=self.list).exists())

    def test_create_list(self):
        """ Test create list """
        name = "New list"
        data = {
            'new': name,
            '_method': 'put'
        }

        response = self.client.post(reverse(
            'lists:manage_lists'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(List.objects.filter(user=self.normal_user,
                                            name=name).exists())

    def test_update_list(self):
        """ Test update existing list's name """
        name = "New name"
        field_name = "list{}".format(self.list.id)
        data = {
            'fieldChange': self.list.id,
            field_name: name,
            '_method': 'put'
        }

        response = self.client.post(reverse(
            'lists:manage_lists'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(List.objects.filter(id=self.list.id,
                                            name=name).exists())

    def test_delete_list(self):
        """ Test delete existing list """
        data = {
            'dellist': [self.list.id],
            '_method': 'delete'
        }

        response = self.client.post(reverse(
            'lists:manage_lists'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertFalse(List.objects.filter(id=self.list.id).exists())