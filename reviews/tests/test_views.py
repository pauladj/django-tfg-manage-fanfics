from unittest import mock

from django.test import TestCase, Client
from django.urls import reverse

from common.models import Fanfic, Review
from users.models import CustomUser


class ReviewViewTest(TestCase):
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
        self.review = Review.objects.create(score=3, fanfic=self.fanfic,
                                            user=self.normal_user)

        self.client = Client()
        self.client.force_login(user=self.normal_user)

    def test_review_edit_page_status_code(self):
        """ Test get edit page for review """
        response = self.client.get(reverse(
            'reviews:review', kwargs={'review_id': self.review.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review.html')

    def test_update_review(self):
        """ Test update review """
        text = "test text"

        response = self.client.post(reverse(
            'reviews:review', kwargs={'review_id': self.review.id}),
            {'_method': 'put', 'text': text, 'stars': 3}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review.html')

        updated_review = Review.objects.get(id=self.review.id)
        self.assertEqual(updated_review.text, text)
        self.assertEqual(updated_review.score, 3)

    def test_update_review_stars_error(self):
        """ Test update review """
        text = "test text"

        response = self.client.post(reverse(
            'reviews:review', kwargs={'review_id': self.review.id}),
            {'_method': 'put', 'text': text, 'stars': 30})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review.html')

        updated_review = Review.objects.get(id=self.review.id)
        self.assertNotEqual(updated_review.score, 30)

    def test_update_review_text_empty(self):
        """ Test update review """
        text = ""

        response = self.client.post(reverse(
            'reviews:review', kwargs={'review_id': self.review.id}),
            {'_method': 'put', 'text': text, 'stars': 3})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review.html')

        updated_review = Review.objects.get(id=self.review.id)
        self.assertNotEqual(updated_review.text, text)

    def test_see_review_status_code(self):
        """ Test see a review  """
        response = self.client.get(reverse(
            'reviews:reviews', kwargs={'review_id': self.review.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review.html')

    def test_create_review_when_already_exists(self):
        """ Test Create new review """
        text = "test text2"

        response = self.client.post(reverse(
            'reviews:reviews'),
            {'fanfic_id': self.fanfic.id, 'text': text, 'stars': 3})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review.html')

        updated_review = Review.objects.get(id=self.review.id)
        self.assertNotEqual(updated_review.text, text)

    def test_create_review(self):
        """ Test Create new review """
        text = "test text2"

        self.review.delete()

        response = self.client.post(reverse(
            'reviews:reviews'),
            {'fanfic_id': self.fanfic.id, 'text': text, 'stars': 3},
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fanfic.html')

        updated_review = Review.objects.get(fanfic=self.fanfic,
                                            user=self.normal_user)
        self.assertEqual(updated_review.text, text)

    def test_delete_review(self):
        """ Test Delete a review """

        response = self.client.delete(reverse(
            'reviews:reviews', kwargs={'review_id': self.review.id}),
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fanfic.html')

        exists = Review.objects.filter(fanfic=self.fanfic,
                                       user=self.normal_user).exists()
        self.assertFalse(exists)
