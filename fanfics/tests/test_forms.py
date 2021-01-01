from django.test import TestCase

from fanfics.forms.web_forms import UserSubmittedErrorForm


class UserSubmittedErrorFormTest(TestCase):

    def test_valid_form(self):
        """ Create error form """
        data = {'issue': "o", 'comment': "Test comment"}
        form = UserSubmittedErrorForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_issue(self):
        """ Create error with invalid issue """
        data = {'issue': "p", 'comment': "Test comment"}
        form = UserSubmittedErrorForm(data=data)
        self.assertFalse(form.is_valid())