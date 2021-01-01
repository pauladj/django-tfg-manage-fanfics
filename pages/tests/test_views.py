from django.http import HttpRequest
from django.test import SimpleTestCase
from django.urls import reverse


class HomePageTests(SimpleTestCase):

    def test_home_page_status_code(self):
        response = self.client.get(reverse('pages:home'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        response = self.client.get(reverse('pages:home'))
        self.assertTemplateUsed(response, 'home.html')
