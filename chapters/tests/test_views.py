import json
from unittest import mock

from django.test import TestCase, Client
from django.urls import reverse

from common.models import Fanfic, Chapter, Reading
from users.models import CustomUser


class ChaptersNotesViewTests(TestCase):

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
        self.chapter = Chapter.objects.create(title="Whatever", num_chapter=1,
                                              url_chapter="url",
                                              fanfic=self.fanfic)

        self.reading = Reading.objects.create(chapter=self.chapter,
                                              user=self.normal_user,
                                              read=False)

        self.client = Client()
        self.client.force_login(user=self.normal_user)

    def test_delete_private_notes(self):
        """ Test clear private notes of user for one fanfic"""
        response = self.client.delete(reverse(
            'chapters_fanfics:chapters_notes',
            kwargs={
                'fanfic_id': self.fanfic.id}),
            follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fanfic.html')

        readings = Reading.objects.filter(chapter__fanfic=self.fanfic,
                                          user=self.normal_user,
                                          private_notes__isnull=False).count()

        self.assertEqual(readings, 0)

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_create_edit_private_note(self, mock_is_ajax):
        """ Test Create/edit message"""
        mock_is_ajax.return_value = True
        response = self.client.post(reverse(
            'chapters_fanfics:chapters_note',
            kwargs={
                'fanfic_id': self.fanfic.id,
                'chapter_id': self.chapter.id}
        ), {"text": "this is a "
                    "test "
                    "private note"})

        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['success'], True)

        response = self.client.post(reverse(
            'chapters_fanfics:chapters_note',
            kwargs={
                'fanfic_id': self.fanfic.id,
                'chapter_id': self.chapter.id}
        ), {"text": "this is a "
                    "test "
                    "private note"})

        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['success'], True)

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_create_edit_private_note_empty(self, mock_is_ajax):
        """ Test Create/edit message"""
        mock_is_ajax.return_value = True
        response = self.client.post(reverse(
            'chapters_fanfics:chapters_note',
            kwargs={
                'fanfic_id': self.fanfic.id,
                'chapter_id': self.chapter.id}
        ), {"text": ""})

        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['success'], True)


class ChaptersViewTests(TestCase):

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
        self.chapter = Chapter.objects.create(title="Whatever", num_chapter=1,
                                              url_chapter="url",
                                              fanfic=self.fanfic)

        self.client = Client()
        self.client.force_login(user=self.normal_user)

    def test_delete_all(self):
        """ Test Clear all the data of one user for one fanfic"""
        response = self.client.delete(reverse(
            'chapters_fanfics:chapters', kwargs={'fanfic_id': self.fanfic.id}),
            follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fanfic.html')

        readings = Reading.objects.filter(chapter__fanfic=self.fanfic,
                                          user=self.normal_user).count()

        self.assertEqual(readings, 0)

    def test_mark_all_as_read(self):
        """ Test Mark all chapters as read """
        response = self.client.post(reverse(
            'chapters_fanfics:chapters',
            kwargs={'fanfic_id': self.fanfic.id}), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fanfic.html')

        readings = Reading.objects.filter(chapter__fanfic=self.fanfic,
                                          user=self.normal_user,
                                          read=False).count()

        self.assertEqual(readings, 0)

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_mark_chapter_as_read_unread(self, mock_is_ajax):
        """ Test Mark chapter as read/unread """
        mock_is_ajax.return_value = True
        response = self.client.post(reverse(
            'chapters_fanfics:chapter_mark',
            kwargs={
                'fanfic_id': self.fanfic.id,
                'chapter_id': self.chapter.id}
        ))

        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['success'], True)

    @mock.patch('django.core.handlers.wsgi.WSGIRequest.is_ajax')
    def test_mark_chapter_as_read(self, mock_is_ajax):
        """ Test Mark last chapter of fanfic and user as read """
        mock_is_ajax.return_value = True
        response = self.client.post(reverse(
            'chapters_fanfics:chapter_read',
            kwargs={
                'fanfic_id': self.fanfic.id}
        ))

        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['success'], True)
        self.assertTrue(Reading.objects.filter(user=self.normal_user,
                                               chapter=self.chapter,
                                               read=True).exists())
