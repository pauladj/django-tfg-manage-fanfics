from django.test import SimpleTestCase, TestCase
from common.utils import clean_string
from fanfics.custom_models import FanficWeb as Fanfic
from unittest import mock


class CleanStringTests(SimpleTestCase):

    def test_clean_normal_string(self):
        text = "this is an example"
        self.assertEqual(clean_string(text), text)

    def test_clean_empty_string(self):
        text = ""
        self.assertEqual(clean_string(text), None)
