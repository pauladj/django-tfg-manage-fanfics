from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from common.models import Type
from users.models import CustomUser


class FandomsViewTest(TestCase):

    def setUp(self):
        self.normal_user = CustomUser.objects.create(
            name_surname="name",
            country="AM",
            date_of_birth="2000-07-02",
            email="em@gm.com",
            username='testuser',
            password="12345")
        self.type = Type.objects.create(name="testtype")

        self.client = Client()
        self.client.force_login(user=self.normal_user)

    def test_fandoms_of_media_type_status_code(self):
        response = self.client.get(reverse('media_type:fandoms',
                                           kwargs={'media_type':
                                                       self.type.name}
                                           ))
        self.assertEqual(response.status_code, 200)
